# historical-options-database
A simple script to pull options data from the tdameritrade api and stores it in an sqlite3 database. Can be configured for a range of strikes and expiries. The greeks are stored as well.

Execute the script as a cron job to run on the 30th minute of every hour via `crontab -e` (macOS only)
## cron

```
30 * * * * /Library/Frameworks/Python.framework/Versions/3.7/bin/python3 /Users/desmond/tdameritrade/options.py >> history.log 2>&1
```

## Requirements
 - An approved TD Ameritrade account + consumer key
 - tda-api via `pip3 install tda-api`
 - sqlite3
 
