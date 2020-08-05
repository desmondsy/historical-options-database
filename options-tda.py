from tda import auth, client
from pprint import pprint
from datetime import datetime as dt
import json
import config
import datetime
import sqlite3

def get_lastprice(ticker):
    quote_response = c.get_quote(ticker).json()
    lastprice = quote_response[ticker]['lastPrice']
    return lastprice

def drop_if_exists():
    to_table = ['call','put'] 
    for t in ticker:
        for i in to_table:
            cursor.execute("""
                DROP TABLE IF EXISTS {}_{}_option_history
            """.format(t,i))

def create_calls_table(ticker):
    try:
        cursor.execute("""
            CREATE TABLE {}_call_option_history(
                timestamp text,
                underlying text,
                symbol text,
                description text,
                strike real,
                current_underlying real,
                bid real,
                ask real,
                last real,
                delta real,
                gamma real,
                theta real,
                vega real
            )
        """.format(ticker))
    except:
        pass

def create_puts_table(ticker):
    try:
        cursor.execute("""
            CREATE TABLE {}_put_option_history(
                timestamp text,
                underlying text,
                symbol text,
                description text,
                strike real,
                current_underlying real,
                bid real,
                ask real,
                last real,
                delta real,
                gamma real,
                theta real,
                vega real
            )
        """.format(ticker))
    except:
        pass

def option_database(ticker,contract_type,start_date,end_date,strike_no):
    response = c.get_option_chain(ticker, 
                                contract_type=contract_type,
                                strike_from_date=start_date,
                                strike_to_date=end_date,
                                strike_count=strike_no)

    json_response = json.dumps(response.json(), indent=4)
    options_dict = json.loads(json_response)
    if options_dict['status'] == 'FAILED':
        raise Exception('Check input params!')

    if contract_type == c.Options.ContractType.CALL:
        options_dict = options_dict['callExpDateMap']
        to_table = 'call'
    if contract_type == c.Options.ContractType.PUT:
        options_dict = options_dict['putExpDateMap']
        to_table = 'put'

    time_now = dt.now().replace(second=0, microsecond=0).isoformat()

    for k in options_dict.keys():
        for strike in options_dict[k]:
            for option in options_dict[k][strike]:
                data = (time_now,ticker,option['symbol'], option['description'],option['strikePrice'], get_lastprice(ticker),option['bid'], option['ask'], option['last'],option['delta'], option['gamma'], option['theta'], option['vega'])
                print(",".join(map(str,data)))

                cursor.execute("""
                    INSERT INTO {}_{}_option_history (
                        timestamp,
                        underlying,
                        symbol,
                        description,
                        strike,
                        current_underlying,
                        bid,
                        ask,
                        last,
                        delta,
                        gamma,
                        theta,
                        vega
                    )
                    VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                """.format(ticker,to_table), data)

connection = sqlite3.connect("option_history.db")
cursor = connection.cursor()

# TDAmeritrade Auth
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path=config.chromedriver_path) as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)

ticker = ['SLV']
start_date = datetime.datetime.strptime('2020-08-01', '%Y-%m-%d').date()
end_date = datetime.datetime.strptime('2020-08-30', '%Y-%m-%d').date()
contract_type = [c.Options.ContractType.CALL,c.Options.ContractType.PUT]
strike_no = 5

#drop_if_exists()

for t in ticker:
    create_calls_table(t)
    create_puts_table(t)


    for i in range(len(contract_type)):
        option_database(t,contract_type[i],start_date,end_date,strike_no)
        connection.commit()

connection.close() 

