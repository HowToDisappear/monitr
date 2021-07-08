import asyncio
import aiopg


async def foo(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as curs:
            while True:
                await curs.execute("""
                SELECT AVG( last_price ) AS BTCUSDT_avg_binance
                FROM crypto
                WHERE symbol = 'BTCUSDT' AND exchange = 'binance';
                """)
                avg = await curs.fetchone()
                print(f"Binance BTCUSDT avg: {round(avg[0], 2)}")
                await asyncio.sleep(2)


async def bar(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as curs:
            while True:
                await curs.execute("""
                SELECT AVG( last_price ) AS BTCUSDT_avg_kucoin
                FROM crypto
                WHERE symbol = 'BTCUSDT' AND exchange = 'kucoin';
                """)
                avg = await curs.fetchone()
                print(f"KuCoin BTCUSDT avg: {round(avg[0], 2)}")
                await asyncio.sleep(2)


async def main():
    async with aiopg.create_pool(dsn=f"dbname=monitr host=127.0.0.1") as pool:
        task1 = asyncio.create_task(foo(pool))
        task2 = asyncio.create_task(bar(pool))
        await asyncio.gather(task1, task2)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

