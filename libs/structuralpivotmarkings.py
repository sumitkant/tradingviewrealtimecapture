import pandas as pd
import numpy as np
from itertools import combinations

# marking SPL
def getSPL(df, main_df, lastSPHbar):
    # higher closes
    if (df.iloc[2].close > df.iloc[0].close) & (df.iloc[1].close > df.iloc[0].close):
        # higher highs
        if (df.iloc[2].high > df.iloc[0].high) & (df.iloc[1].high > df.iloc[0].high):
            B2 = df.iloc[2].bar
            B1 = df.iloc[1].bar
            A = df.iloc[0].bar
            temp_df = main_df.loc[lastSPHbar + 1: B2]
            minLow = temp_df.low.min()
            P = temp_df.loc[temp_df.low == minLow, 'bar'].index[0]
            print('SPL Found @', P, 'New Anchor @', B2, 'Lowest :', minLow)
            return A, B1, B2, P


# marking SPH
def getSPH(df, main_df, lastSPLbar):
    # lower closes
    if (df.iloc[2].close < df.iloc[0].close) & (df.iloc[1].close < df.iloc[0].close):
        # lower lows
        if (df.iloc[2].low < df.iloc[0].low) & (df.iloc[1].low < df.iloc[0].low):
            B2 = df.iloc[2].bar
            B1 = df.iloc[1].bar
            A = df.iloc[0].bar
            temp_df = main_df.loc[lastSPLbar + 1: B2]
            maxHigh = temp_df.high.max()
            P = temp_df.loc[temp_df.high == maxHigh, 'bar'].index[0]
            print('SPH Found @', P, 'New Anchor @', B2, 'Highest :', maxHigh)
            return A, B1, B2, P



def mark_all_pivots(master_df, datetime_col):

    # read dataset
    master_df = master_df.rename(columns ={datetime_col:'datetime'})
    master_df['date'] = pd.to_datetime(master_df['datetime']).dt.date
    master_df['bar'] = master_df.reset_index(drop=True).index

    # parameter initialize
    start_bar = 0  # Next Anchor
    SPL = False  # if this is False, it will look for SPH
    k = 35  # finds SPH/SPL in the next 25 bar combinations
    lastpivot_bar = 0  # location of immidiately previous SPH/SPL
    master_df['SMALL_PIVOTS'] = 0  # -1 for SPL, 1 for SPH and 0 for no pivot
    master_df['SPH_bars'] = np.nan
    master_df['SPL_bars'] = np.nan

    # iterating over dataset - marking small pivots
    for i in range(master_df.shape[0] - 2):

        try:
            # if pivot_found then it breaks the loop - set for False for looking for SPH/SPL
            pivot_found = False

            # combinations of 3 bars sorted by the sum of locations. 1st bar in combination of 3 will always be Anchor
            combis = sorted(combinations(np.arange(start_bar, start_bar + 3 + k), 3), key=sum)
            combis = sorted(combis, key=max)

            # iterate over all combinations
            for c in combis:

                lookup_df = master_df.loc[list(c)]
                # print('Trying combination :', c)

                try:
                    # if SPL is set to True, that means look for SPL else look for SPH
                    if SPL:
                        a, b1, new_anchor, pivot_pt = getSPL(lookup_df, master_df, lastpivot_bar)
                        start_bar = new_anchor  # new anchor B2 of previous SPH
                        lastpivot_bar = pivot_pt  # Location updated since SPL found
                        SPL = False  # set to false to stop looking for SPL
                        master_df.loc[pivot_pt, 'SMALL_PIVOTS'] = -1  # updated dataset
                        master_df.loc[a, 'SPL_bars'] = 'A'  # updated dataset
                        master_df.loc[b1, 'SPL_bars'] = '1'  # updated dataset
                        master_df.loc[new_anchor, 'SPL_bars'] = '2'  # updated dataset
                        master_df.loc[pivot_pt, 'SP_FORMED_AT'] = master_df.loc[new_anchor, 'datetime']
                        master_df.loc[pivot_pt, 'SP_FORMED_AT_CLOSE'] = master_df.loc[new_anchor, 'close']
                        pivot_found = True

                    else:
                        a, b1, new_anchor, pivot_pt = getSPH(lookup_df, master_df, lastpivot_bar)
                        start_bar = new_anchor  # new anchor B2 of previous SPL
                        lastpivot_bar = pivot_pt  # Location updated since SPH found
                        SPL = True
                        master_df.loc[pivot_pt, 'SMALL_PIVOTS'] = 1
                        master_df.loc[a, 'SPH_bars'] = 'A'  # updated dataset
                        master_df.loc[b1, 'SPH_bars'] = '1'  # updated dataset
                        master_df.loc[new_anchor, 'SPH_bars'] = '2'  # updated dataset
                        master_df.loc[pivot_pt, 'SP_FORMED_AT'] = master_df.loc[new_anchor, 'datetime']
                        master_df.loc[pivot_pt, 'SP_FORMED_AT_CLOSE'] = master_df.loc[new_anchor, 'close']
                        pivot_found = True

                except Exception as e:
                    pass

                if pivot_found:                # break loop if pivot found

                    break

            if start_bar >= master_df.shape[0] - 2:
                break

        except KeyError:
            break

    # plotting bars
    master_df['datetime_formatted'] = pd.to_datetime(master_df['datetime']).dt.strftime('%H:%M %m-%d-%Y')

    master_df['pivot_text'] = np.nan
    master_df.loc[master_df.SMALL_PIVOTS == -1, 'pivot_text'] = 'SPL'
    master_df.loc[master_df.SMALL_PIVOTS == 1, 'pivot_text'] = 'SPH'

    master_df['pivot_y'] = (master_df.low + master_df.high) / 2
    master_df['pivot_y'][master_df.SMALL_PIVOTS == -1] = master_df.low - 30
    master_df['pivot_y'][master_df.SMALL_PIVOTS == 1] = master_df.high + 25

    # ------------------------------ LARGE PIVOT MARKINGS ------------------------------ #

    # read small pivot markings
    master = master_df.copy()

    # Find whether current SPH was broken
    sph = master.loc[master.pivot_text == 'SPH'][['datetime', 'pivot_text', 'high']]
    sph['next_sph'] = sph.high.shift(-1)
    sph['broken_sph'] = (sph.next_sph > sph.high).astype(int)

    # Find whether current SPL was broken
    spl = master.loc[master.pivot_text == 'SPL'][['datetime', 'pivot_text', 'low']]
    spl['next_spl'] = spl.low.shift(-1)
    spl['broken_spl'] = (spl.next_spl < spl.low).astype(int)

    master = (master
              .merge(sph[['datetime', 'broken_sph']], on='datetime', how='left')
              .merge(spl[['datetime', 'broken_spl']], on='datetime', how='left'))

    # Broken Small Pivot - combines SPH, SPL breaks
    master.broken_sph.fillna(0, inplace=True)
    master.broken_spl.fillna(0, inplace=True)
    master['broken'] = master[['broken_sph', 'broken_spl']].max(axis=1)

    # Identifies when the SPH or SPL was broken
    pivots = master[~master.pivot_text.isnull()][['datetime']].reset_index()
    pivots['next_pivot'] = pivots['index'].shift(-1)
    pivots['next_same_pivot'] = pivots['index'].shift(-2)
    master = master.merge(pivots, on='datetime', how='left')

    for i in range(master.shape[0]):
        if master.loc[i, 'broken'] == 1:
            if master.loc[i, 'pivot_text'] == 'SPH':
                high = master.loc[i, 'high']
                df = master.loc[master.loc[i, 'next_pivot']: master.loc[i, 'next_same_pivot']][['datetime', 'high']]
                for j in df.index:
                    if df.loc[j, 'high'] > high:
                        master.loc[i, 'broken_at'] = df.loc[j, 'datetime']
                        break
            else:
                low = master.loc[i, 'low']
                df = master.loc[master.loc[i, 'next_pivot']: master.loc[i, 'next_same_pivot']][['datetime', 'low']]
                for j in df.index:
                    if df.loc[j, 'low'] < low:
                        master.loc[i, 'broken_at'] = df.loc[j, 'datetime']
                        break

    # Identifies the broken pivot was first of its kind to be broken
    broken_cnt = master[master.pivot_text.isin(['SPH', 'SPL']) & (master.broken == 1)][
        ['datetime', 'pivot_text', 'broken']]
    broken_cnt['prev_pivot'] = broken_cnt.pivot_text.shift(1)
    broken_cnt['break_order'] = (broken_cnt.prev_pivot != broken_cnt.pivot_text).astype(int)

    master = master.merge(broken_cnt[['break_order']], left_index=True, right_index=True, how='left')
    master.break_order.fillna(0, inplace=True)
    print(master[['datetime', 'high', 'low', 'pivot_text', 'broken', 'break_order']].head(10))

    # Setting Looking for LPH, LPL to True depending on which small pivot was broken
    start_loc = 0
    lookup_start = master[(master.pivot_text.isin(['SPH', 'SPL'])) & (master.broken == 1)]
    if lookup_start.iloc[0]['pivot_text'] == 'SPH':
        LPL, LPH = True, False
    else:
        LPL, LPH = False, True

    # Marking Large Pivots -  Looks at series of SPH after an SPL
    # break to mark the highest point as LPH and vice versa for LPL

    for i in range(master.shape[0]):
        if i >= start_loc:
            if LPL:
                print('Looking for LPL')
                if (master.loc[i, 'pivot_text'] == 'SPH') & (master.loc[i, 'broken'] == 1) & (
                        master.loc[i, 'break_order'] == 1):
                    break_loc = master[master.datetime == master.loc[i, 'broken_at']].index[0]
                    df = master.loc[start_loc:break_loc]
                    min_lpl = df[df.pivot_text == 'SPL'].low.min()
                    lpl_loc = df[(df.pivot_text == 'SPL') & (df.low == min_lpl)].index[0]
                    print(start_loc, break_loc, lpl_loc)
                    master.loc[lpl_loc, 'LARGE_PIVOT'] = 'LPL'
                    start_loc = lpl_loc
                    LPL, LPH = False, True
            else:
                print('Looking for LPH')
                if (master.loc[i, 'pivot_text'] == 'SPL') & (master.loc[i, 'broken'] == 1) & (
                        master.loc[i, 'break_order'] == 1):
                    break_loc = master[master.datetime == master.loc[i, 'broken_at']].index[0]
                    df = master.loc[start_loc:break_loc]
                    max_lph = df[df.pivot_text == 'SPH'].high.max()
                    lph_loc = df[(df.pivot_text == 'SPH') & (df.high == max_lph)].index[0]
                    print(start_loc, break_loc, lph_loc)
                    master.loc[lph_loc, 'LARGE_PIVOT'] = 'LPH'
                    start_loc = lph_loc
                    LPL, LPH = True, False

    # saving markings to csv
    # master.to_csv('PIVOT_MARKINGS.csv', index=False)

    return master
