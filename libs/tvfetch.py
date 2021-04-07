import json
import pandas as pd
from datetime import timedelta, time
from websocket import create_connection
from libs.tvstreamhelper import generateSession, generateChartSession, sendMessage

# Initialize the headers needed for the websocket connection
def tv_headers():
    headers = json.dumps({
        'Origin': 'https://data.tradingview.com'
    })
    return headers

# Then create a connection to the tunnel
def newSession():
    ws = create_connection(
        'wss://data.tradingview.com/socket.io/websocket',
        headers=tv_headers()
    )
    session = generateSession()
    chart_session = generateChartSession()
    return ws, session, chart_session

def messagebox(ws, session, chart_session, ticker, resolution, bars):
    sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
    sendMessage(ws, "chart_create_session", [chart_session, ""])
    sendMessage(ws, "quote_create_session", [session])
    sendMessage(ws, "quote_set_fields", [session, "ch", "chp", "current_session", "description", "local_description",
                                         "language", "exchange", "fractional", "is_tradable", "lp", "lp_time",
                                         "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name",
                                         "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
    sendMessage(ws, "quote_add_symbols", [session, ticker, {"flags": ['force_permission']}])
    sendMessage(ws, "quote_fast_symbols", [session, ticker])
    sendMessage(ws, "resolve_symbol", [chart_session,"symbol_1", "={\"symbol\":\"" + ticker + "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
    sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", resolution, bars])

def search_data(ticker, resolution, bars):
    ws, session, chart_session = newSession()
    messagebox(ws, session, chart_session, ticker, resolution, bars)

    search_tu = True
    while search_tu:
        try:
            result = ws.recv()
            result = result.split('~')

            for item in result:
                if 'timescale_update' in item:
                    item = pd.DataFrame([x['v'] for x in json.loads(item)['p'][1]['s1']['s']])
                    item.columns = ['epochtime', 'open', 'high', 'low', 'close', 'volume']
                    item['datetime'] = pd.to_datetime(item.epochtime, unit='s') + timedelta(hours=5.5)
                    item['time'] = item.datetime.dt.time
                    # considering time between 9:15 AM and 3:30 PM
                    item = item[item.time.between(time(9,15), time(15,30), inclusive=True)]
                    # removing rows where OHLC values are same
                    item = item[item[['open', 'high', 'low', 'close']].std(axis=1) > 0]
                    return item
                    search_tu = False

        except Exception as e:
            item = ''
            return item

def fetch_raw_data(ticker, resolution, bars):
    ws, session, chart_session = newSession()
    messagebox(ws, session, chart_session, ticker, resolution, bars)

    search_tu = True
    while search_tu:
        try:
            result = ws.recv()
            result = result.split('~')

            for item in result:
                if 'timescale_update' in item:
                    item = pd.DataFrame([x['v'] for x in json.loads(item)['p'][1]['s1']['s']])
                    item.columns = ['epochtime', 'open', 'high', 'low', 'close', 'volume']
                    item['datetime'] = pd.to_datetime(item.epochtime, unit='s') + timedelta(hours=5.5)
                    item['time'] = item.datetime.dt.time
                    return item

        except Exception as e:
            item = ''
            return item
