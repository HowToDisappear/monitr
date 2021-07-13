# monitr
Monitr app collects market data from several cryptocurrency exchanges (i.e. 'Binace' and 'KuCoin') in 
real-time and stores it into a database. The data is obtained through WebSocket stream APIs.
As a backing store we use PostgreSQL rdbms.
Other apps/ scripts are free to access the database the same time the monitr is running.
Use cases for the data would be trading, building dashboards etc.
### Set up
I suggest using venv or container for the set up for your convenience.
* first, clone this repo to your venv
* in your venv run ```deploy.sh``` script that is going to install all necessary Python dependencies
* then you need to set up a PostgreSQL database. Install (if you have not already) PostgreSQL and psql command line tool. See here: https://www.postgresql.org/
* once you have PostgreSQL ready, create the database with ```psql -c "CREATE DATABASE monitr"```
* then create the tables for the db from the script with ```psql monitr < init.sql```

Now you are all set.
### Usage
Just run ```core.py``` in your terminal, you will see several status messages and market data will start floating into your postgres database. You can access it live with psql tool or programmatically through a script or another app (you can try out our short ```example_access.py```). Script is stopped normally by ```Ctrl-C```. 
