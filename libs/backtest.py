import pandas as pd
df = pd.read_csv('PIVOT_MARKINGS.csv')
df.columns = df.columns.str.strip()

pd.options.display.max_columns = 999

df.fillna('', inplace=True)

df.head(20)

POS = 0
TARGET_PC = 0.01
SL_PC = 0.0025
CAPITAL = 200000
LOT = 1
LOTSIZE = 25
LEVERAGE = 0.22

for i in range(df.shape[0]):

    if POS == 0:

        if df.loc[i, 'LP_REALIZED'] == 'LPL':

            POS = 1
            entry_price = df.loc[i, 'CLOSE']
            target_price = entry_price * (1 + TARGET_PC)
            sl_price = entry_price * (1 - SL_PC)
            turnover = entry_price * LOT * LOTSIZE
            CAPITAL -= turnover
            PNL = 0
            print("""
            ----------------------------------------
            TRADE    : LONG
            ENTRY    : {}
            TARGET   : {}
            SL       : {}
            TURNOVER : {}
            """.format(round(entry_price, 2), round(target_price, 2), round(sl_price, 2), round(turnover, 2)))


        elif df.loc[i, 'LP_REALIZED'] == 'LPH':

            POS = -1
            entry_price = df.loc[i, 'CLOSE']
            target_price = entry_price * (1 - TARGET_PC)
            sl_price = entry_price * (1 + SL_PC)
            turnover = entry_price * LOT * LOTSIZE
            CAPITAL += turnover
            PNL = 0

            print("""
            ----------------------------------------
            TRADE    : SHORT
            ENTRY    : {}
            TARGET   : {}
            SL       : {}
            TURNOVER : {}
            """.format(round(entry_price, 2), round(target_price, 2), round(sl_price, 2), round(turnover, 2)))

    if POS == 1:

        if df.loc[i - 1, 'LOW'] <= sl_price:

            turnover = sl_price * LOT * LOTSIZE
            CAPITAL += turnover
            PNL = (sl_price - entry_price) * LOT * LOTSIZE
            POS = 0
            print("""
            TRADE    : LONG SL HIT
            EXIT     : {}
            TURNOVER : {}
            P&L      : {}
            ----------------------------------------
            """.format(round(sl_price, 2), round(turnover, 2), round(PNL, 2)))

        elif df.loc[i, 'HIGH'] >= target_price:

            turnover = target_price * LOT * LOTSIZE
            CAPITAL += turnover
            PNL = (target_price - entry_price) ** LOT * LOTSIZE
            POS = 0
            print("""
            TRADE    : LONG TARGET HIT
            EXIT     : {}
            TURNOVER : {}
            ----------------------------------------
            """.format(round(target_price, 2), round(turnover, 2), round(PNL, 2)))

    if POS == -1:

        if df.loc[i - 1, 'HIGH'] >= sl_price:

            turnover = sl_price * LOT * LOTSIZE
            CAPITAL -= turnover
            PNL = (sl_price - entry_price) ** LOT * LOTSIZE
            POS = 0
            print("""
            TRADE    : SHORT SL HIT
            EXIT     : {}
            TURNOVER : {}
            ----------------------------------------
            """.format(round(sl_price, 2), round(turnover, 2), round(PNL, 2)))

        elif df.loc[i, 'LOW'] <= target_price:

            turnover = target_price * LOT * LOTSIZE
            CAPITAL -= turnover
            PNL = (target_price - entry_price) ** LOT * LOTSIZE
            POS = 0
            print("""
            TRADE    : SHORT TARGET HIT
            EXIT     : {}
            TURNOVER : {}
            ----------------------------------------
            """.format(round(target_price, 2), round(turnover, 2), round(PNL, 2)))


