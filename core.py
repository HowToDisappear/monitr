import asyncio
import json
from datetime import datetime
import websockets
import aiopg
import requests
import binance_const as bn


BN_ENDPOINT = "wss://stream.binance.com:9443/ws"
BN_STREAMS = [
    bn.BTC_STR,
    bn.BNB_STR + bn.ETH_STR + bn.TRX_STR + bn.XRP_STR + bn.ETF_STR,
    bn.FIAT_STR[:326],
    bn.FIAT_STR[326:],
]
KC_TOKEN_URI = "https://api.kucoin.com/api/v1/bullet-public"
DBNAME = "monitr"
DBHOST = "127.0.0.1"


async def bn_create_connections():
    """ Creates websocket connections to Binance API """
    bn_websockets = []
    for i in range(len(BN_STREAMS)):
        bn_websockets.append(await websockets.connect(BN_ENDPOINT))
        print(f'connected to BINANCE at {bn_websockets[i].remote_address}')
    return bn_websockets


async def kc_create_connections():
    """ Creates websocket connections to KuCoin API """
    kc_token_req = requests.post(KC_TOKEN_URI)
    kc_token = json.loads(kc_token_req.content)['data']['token']
    kc_endpoint = json.loads(kc_token_req.content)['data']['instanceServers'][0]['endpoint']
    kc_endpoint = f"{kc_endpoint}?token={kc_token}"
    ws = await websockets.connect(kc_endpoint)
    reply = json.loads(await ws.recv())
    kc_websockets = []
    if reply['type'] == 'welcome':
        print(f'connected to KUCOIN at {ws.remote_address}')
        kc_websockets.append(ws)
    else:
        print(f"failed to connect to KUCOIN:\n{reply}")
    return kc_websockets


async def bn_subscribe(bn_websockets):
    """ Sends subscription requests for market data streams """
    print(f'subscribing to BINANCE...')
    for i in range(len(BN_STREAMS)):
        await bn_websockets[i].send(json.dumps(
            {
                "method": "SUBSCRIBE",
                "params": BN_STREAMS[i],
                "id": i+1,
            }
        ))


async def kc_subscribe(kc_websockets):
    """ Sends subscription request for market data stream """
    print(f'subscribing to KUCOIN...')
    await kc_websockets[0].send(json.dumps(
        {
            "id": 12345,
            "type": "subscribe",
            "topic": "/market/ticker:all",
            "response": True
        }
    ))


async def pg_client(pool, queue):
    """ Gets data item out of the queue, parses it and inserts it into the DB """
    async with pool.acquire() as conn:
        async with conn.cursor() as curs:
            while True:
                exchange, stream = await queue.get()
                if exchange == "binance":
                    data = json.loads(stream)
                    symbol = data['s']
                    base, quote = bn.SYM_TABLE[symbol]
                    price = data['p']
                    time = datetime.fromtimestamp(data['T'] / 1000.0)
                    entry = ("binance", symbol, base, quote, price, time)
                elif exchange == "kucoin":
                    data = json.loads(stream)
                    base, quote = data['subject'].split('-')
                    symbol = base + quote
                    price = data['data']['price']
                    time = datetime.fromtimestamp(data['data']['time'] / 1000.0)
                    entry = ("kucoin", symbol, base, quote, price, time)

                await curs.execute("""
                INSERT INTO crypto (exchange, symbol, base, quote, last_price, time_received)
                VALUES (%s, %s, %s, %s, %s, %s)""", entry)
                queue.task_done()


async def ws_client(websocket, queue, exchange):
    """ Reads in data item from the websocket and puts it into the queue """
    status = json.loads(await websocket.recv())
    if exchange == 'binance':
        if status['result'] is None:
            print(f'successfully subscribed at {websocket.remote_address}')
        else:
            return None
    elif exchange == 'kucoin':
        if status['type'] == 'ack':
            print(f'successfully subscribed at {websocket.remote_address}')
        else:
            return None
    while True:
        stream = await websocket.recv()
        await queue.put((exchange, stream))


async def main():
    bn_websockets = await bn_create_connections()
    kc_websockets = await kc_create_connections()

    async with aiopg.create_pool(dsn=f"dbname={DBNAME} host={DBHOST}", minsize=10, maxsize=20) as pgpool:
        queue = asyncio.Queue()
        producers = ([asyncio.create_task(ws_client(ws, queue, "binance")) for ws in bn_websockets] +
                     [asyncio.create_task(ws_client(ws, queue, "kucoin")) for ws in kc_websockets])
        consumers = [asyncio.create_task(pg_client(pgpool, queue)) for _ in range(20)]

        await bn_subscribe(bn_websockets)
        await kc_subscribe(kc_websockets)

        await asyncio.gather(*producers)
        await queue.join()
        for c in consumers:
            c.cancel()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
