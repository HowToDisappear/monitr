# monitr
Monitr app collects market data from 'Binace' and 'KuCoin' in real-time and stores it into PostgreSQL databse. Other apps can access the databse and use this live data.
### Set up guide
I suggest using venv or container for the set up for your convinience.
* in your venv run ```deploy.sh``` script that is going to install all necessary Python dependencies
* then you need to set up a PostgreSQL database. Install (if you have not already) PostgreSQL and psql command line tool. See here: https://www.postgresql.org/
* once you have PostgreSQL ready, create the database with this command ```psql -c "CREATE DATABASE monitr"``` in your terminal
* then we create the tables for the db from the script with ```psql monitr < init.sql```

Now you are all set and ready.
### Usage
Just run ```core.py``` in your terminal, you will see several status messages and market data will start floating into your postgres database. You can access it live with psql tool or programmatically through a script or another app (you can try out our short example_access.py).
