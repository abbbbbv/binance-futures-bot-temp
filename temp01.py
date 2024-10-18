import time
from datetime import datetime
from binance.client import Client
from binance.um_futures import UMFutures
import logging
from http.client import RemoteDisconnected
from requests.exceptions import ConnectionError, HTTPError

umfutures = UMFutures(key='', secret='')

symbol = ['XRPUSDT'] 
interval = '1m' 

#logging remove if seen unnecessary 
logging.basicConfig(filename='logfile01.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# these functions would be useful when creating a trading bot 


def get_symbol_info(symbol):
    info = umfutures.exchange_info()
    for s in info['symbols']:
        if s['symbol'] == symbol:
            filters = {f['filterType']: f for f in s['filters']}
            price_precision = s['pricePrecision']
            quantity_precision = s['quantityPrecision']
            min_qty = float(filters['LOT_SIZE']['minQty'])
            step_size = float(filters['LOT_SIZE']['stepSize'])
            tick_size = float(filters['PRICE_FILTER']['tickSize'])
            return price_precision, quantity_precision, min_qty, step_size, tick_size
    raise Exception(f"Symbol {symbol} not found in exchange info.")

def get_klines(symbol, interval, limit):
    retries = 0
    while retries < max_retries:
        try:
            return umfutures.klines(symbol=symbol, interval=interval, limit=limit)
        except (ConnectionError, HTTPError, RemoteDisconnected) as e:
            retries += 1
            logging.error(f"Error fetching klines for {symbol}: {e}. Retry {retries}/{max_retries}")
            time.sleep(2 ** retries)  # Exponential backoff
    raise Exception(f"Failed to fetch klines for {symbol} after {max_retries} retries.")

def apply_precision(value, precision):
   return round(value, precision)

def adjust_quantity(quantity, step_size):
    return (quantity // step_size) * step_size


def place_order(symbol, side, quantity):
    retries = 0
    while retries < max_retries:
        try:
            order = umfutures.new_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            logging.info(f"Market order placed: {order}")
            return order
        except Exception as e:
            retries += 1
            logging.error(f"Error placing market order for {symbol}: {e}. Retry {retries}/{max_retries}")
            time.sleep(2 ** retries)  # Exponential backoff
    raise Exception(f"Failed to place market order for {symbol} after {max_retries} retries.")


def place_stop_order(symbol, side, quantity, price, stop_type="STOP_MARKET"):
    retries = 0
    while retries < max_retries:
        try:
            order = umfutures.new_order(
                symbol=symbol,
                side=side,
                type=stop_type,
                quantity=quantity,
                stopPrice=price,
                timeInForce='GTC'
            )
            logging.info(f"{stop_type} order placed: {order}")
            return order
        except Exception as e:
            retries += 1
            logging.error(f"Error placing {stop_type} order for {symbol}: {e}. Retry {retries}/{max_retries}")
            time.sleep(2 ** retries)  # Exponential backoff
    raise Exception(f"Failed to place {stop_type} order for {symbol} after {max_retries} retries.")

def cancel_all_open_orders(symbol):
    try:
        result = umfutures.cancel_open_orders(symbol=symbol)
        logging.info(f"Canceled all open orders for {symbol}: {result}")
    except Exception as e:
        logging.error(f"Error canceling open orders for {symbol}: {e}")


def check_futures_balance():
    try:
        # Fetch the futures account balance
        account_info = umfutures.account()
        
        # Extract relevant balance information
        balances = account_info['assets']
        
        print("Futures Account Balance:")
        for balance in balances:
            asset = balance['asset']
            wallet_balance = balance['walletBalance']
            unrealized_profit = balance['unrealizedProfit']
            print(f"{asset}: Wallet Balance = {wallet_balance}, Unrealized Profit = {unrealized_profit}")
    except Exception as e:
        print(f"An error occurred while fetching futures balance: {e}")

