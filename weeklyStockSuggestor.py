import streamlit as st
import xgboost as xgb
import pandas as pd
from libs.tvfetch import search_data
from sklearn.metrics import roc_auc_score, accuracy_score
import plotly.express as px


def app():
    st.title('Johnny\'s Trading Lab')
    st.image(
        'https://lh3.googleusercontent.com/mjeKcwPO2Hql5uqdBUZAO8Lb6ruOi4j88maoUQvihvSsWrQJs5qF-haMurRrZ0Dv0yKDliuOmOUSqobxpi0hd1bNJVwUDwDMTM_Ln9k=w1400-k',
        caption='Art Generated by AI',
        use_column_width='always'
    )

    c1, c1g, c2 = st.columns((4, 1, 4))
    c1.subheader('Weekly Stock Picker Bot')

    c2.subheader('Data Parameters')
    resolution = c2.selectbox('Ticker Data Resolution',
                              ("1", "3", "5", "10", "15", "30", "60", "120", "240", "D", "W"), 9)
    bars = c2.slider('Bars per Ticker:', 0, 5000, 500, 50)
    sessions = c2.slider('Number of Trading sessions in the resolution:', 0, 100, 5, 5)
    growth_rate = c2.slider('Growth Rate:', 0.00, 1.0, 0.05, 0.01)
    test_size = c2.slider('Test Size:', 0.1, 1.0, 0.2, 0.1)

    c1.markdown(f'''
    Predict stocks in the list of stocks that will grow by more than {growth_rate*100}%  in the next week based on current data
    
    ##### Dependent Variable
    If growth rate in closing price in last {sessions} sessions > {growth_rate*100}% then 1 else 0
    
    ##### Variables
    * OHLC for last {bars} bars
    
    ##### Pipeline
    * Get data from tradingview at a specified resolution
    * split the data in train and test
    * Train XGBoost Model
    * Get Variable importance and results on OOT
    ''')

    st.markdown('''
    ---
    ''')

    # inputs
    tickers = pd.read_csv('libs/tickers.csv', header=None)[0]


    not_used = ['datetime','epochtime','ticker','volume','time','closen','growthn','dep_var']

    def feature_engineer(df):

        # Difference between current prices
        df['open-close'] = df.open - df.close
        df['high-close'] = df.high - df.close
        df['low-close'] = df.low - df.close
        df['high-close'] = df.high - df.low
        df['gap'] = df.open - df.close.shift(1)

        # higher highs
        df['h0-h1'] = df.high - df.high.shift(1)
        df['h0-h2'] = df.high - df.high.shift(2)
        df['h1-h2'] = df.high.shift(1) - df.high.shift(2)

        # higher closes
        df['c0-c1'] = df.close - df.close.shift(1)
        df['c0-c2'] = df.close - df.close.shift(2)
        df['c1-c2'] = df.close.shift(1) - df.close.shift(2)

        # net move up or down
        df['gain'] = (df.close > df.open).astype(int)
        df['loss'] = (df.close <= df.open).astype(int)

        # moving averages
        df['gain7_sum'] = df.gain.rolling(7).sum()
        df['gain7_mean'] = df.gain.rolling(7).mean()
        df['loss7_sum'] = df.loss.rolling(7).sum()
        df['loss7_mean'] = df.loss.rolling(7).mean()

        df['sma7'] = df.close.rolling(7).mean()
        df['sma14'] = df.close.rolling(14).mean()
        df['sma14-sma7'] = df['sma14'] - df['sma7']

        # volume lag
        df['volume_lag'] = df.volume - df.volume.shift(1)

        return df

    # Get data based on inputs
    @st.cache
    def get_ticker_data():
        master, mtrain, mtest, first_closes = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        for ticker in tickers:
            print(ticker)
            temp_df = search_data(ticker, resolution, bars)
            temp_df['ticker'] = ticker
            temp_df.drop(['epochtime', 'time'], inplace=True, axis=1)

            # feature engineer
            temp_df = feature_engineer(temp_df)
            print(temp_df.columns)
            # dep var
            temp_df['closen'] = temp_df.close.shift(-sessions)
            temp_df['growthn'] = temp_df.closen / temp_df.close - 1
            temp_df['dep_var'] = (temp_df.growthn > growth_rate).astype(int)
            temp_df.dropna(inplace=True)

            # normalize features by today's close
            for col in temp_df.columns:
                if col not in not_used + ['close']:
                    temp_df[col] = temp_df[col]/temp_df.close

            # train test split
            train_rows = round(temp_df.shape[0] * (1 - test_size))
            temp_train = temp_df.loc[:train_rows, :]
            temp_test = temp_df.loc[train_rows:, :]

            # create master dataframe for all tickers
            master = master.append(temp_df, ignore_index=True)
            mtrain = mtrain.append(temp_train, ignore_index=True)
            mtest = mtest.append(temp_test, ignore_index=True)

        return master, mtrain, mtest

    # Get overall and train and test data
    dmaster, dtrain, dtest = get_ticker_data()
    #st.dataframe(dmaster.head(10))

    @st.cache
    def get_scoring_data():
        scoring_master = pd.DataFrame()
        for ticker in tickers:
            temp_df = search_data(ticker, resolution, 50)
            temp_df['ticker'] = ticker
            temp_df.drop(['epochtime', 'time'], inplace=True, axis=1)

            # feature engineering
            temp_df = feature_engineer(temp_df)

            temp_df.dropna(inplace=True)
            temp_df = temp_df.tail(20)

            # normalize features by today's close
            for col in temp_df.columns:
                if col not in not_used + ['close']:
                    temp_df[col] = temp_df[col] / temp_df.close

            scoring_master = scoring_master.append(temp_df, ignore_index=True)
        return scoring_master

    # Get Scoring Data
    main_scoring = get_scoring_data()

    # Create copies
    df = dmaster.copy()
    train = dtrain.copy()
    test = dtest.copy()

    # creating dependent variable

    st.title('Exploratory Data Analysis')
    st.markdown('''
    ##### 5 sample rows
    The dataset is normalized by closing price for that day
    ''')
    st.dataframe(df.head(5))

    st.markdown('##### Stocks in Dataset')
    ticks = ', '.join([x.split(':')[1] for x in tickers.tolist()])
    st.write(f'**Total {len(tickers)} Stocks**: {ticks}')

    # selecting variables
    var_list = [
        'open-close',
        'high-close',
        'low-close',
        'gap',
        'h0-h1',
        'h0-h2',
        'h1-h2',
        'c0-c1',
        'c0-c2',
        'c1-c2',
        'sma7',
        'sma14-sma7',
        'volume_lag',
        'gain7_sum',
        'gain7_mean',
        'loss7_sum',
        'loss7_mean',
    ]
    st.markdown('''##### Variables for Modelling''')
    variables = st.multiselect('Select Variables to Model:', var_list, var_list)

    # output train test size and event rates
    st.markdown('##### Event Rates')
    c1, c12g, c2, c23g, c3 = st.columns((3,1,3,1,3))

    c1.title(f'{round(df.dep_var.mean() * 100, 2)}%')
    c1.write(f'Mean Event Rate (Overall) based on {df.shape[0]} bars or {bars / 20:.2f} months of data')

    c2.title(f'{round(train.dep_var.mean() * 100, 2)}%')
    c2.write(f'Mean Event Rate (Train) based on {train.shape[0]} bars or {bars*(1-test_size) / 20:.2f} months of data')

    c3.title(f'{round(test.dep_var.mean() * 100, 2)}%')
    c3.write(f'Mean Event Rate (Test) based on {test.shape[0]} bars or {bars*test_size/ 20:.2f} months of data')

    # correlation matrices
    c1, c2 = st.columns(2)

    c1.markdown('''##### Train Correlation Matrix''')
    fig = px.imshow(round(train[variables].corr(),2), text_auto=True)
    c1.plotly_chart(fig)

    c2.markdown('''##### Train Correlation Matrix''')
    fig = px.imshow(round(test[variables].corr(),2), text_auto=True)
    c2.plotly_chart(fig)

    st.markdown('''
    ---
    # Training Parameters
    ''')

    c1,c2,c3 = st.columns(3)
    eta = c1.slider('ETA:', 0.00, 0.2, 0.03, 0.01)
    max_depth = c2.slider('max_depth:', 1, 10, 5, 1)
    min_child_weight = c3.slider('min_child_weight:', 1, 200, 20, 1)
    num_boost_round = c1.slider('num_boost_round:', 0, 1000, 200, 50)
    colsample_bytree = c2.slider('colsample_bytree:', 0.0, 1.0, 0.8, 0.05)
    gamma = c3.slider('GAMMA:', 0, 50, 20, 1)

    def train_xgb_model(train, test):
        params = {
            'eta': eta,
            'max_depth': max_depth,
            'min_child_weight': min_child_weight,
            'objective': 'binary:logistic',
            'num_boost_round': num_boost_round,
            'colsample_bytree': colsample_bytree,
            'gamma': gamma,
            'eval_metric':'auc'
        }
        train_dm = xgb.DMatrix(train[variables], label=train.dep_var.values)
        test_dm = xgb.DMatrix(test[variables], label=test.dep_var.values)
        model = xgb.train(params, train_dm, num_boost_round=params['num_boost_round'], early_stopping_rounds=None)
        return model, train_dm, test_dm

    model, train_dm, test_dm = train_xgb_model(train, test)

    # Performance Metrics
    def get_performance_metrics(t, tdm, d='TRAIN'):
        t['preds'] = model.predict(tdm)
        temp_metrics = pd.DataFrame({
            'DATA': [d],
            'ROC AUC': [roc_auc_score(t.dep_var, t.preds)],
            'GINI': [2*roc_auc_score(t.dep_var, t.preds) - 1],
            'MEAN ACTUAL': [t.dep_var.mean()],
            'MEAN PREDICTED': [t.preds.mean()]
        })
        return temp_metrics

    # variable importance
    def variable_importance(model):
        fi = pd.DataFrame(model.get_score(importance_type='total_gain'), index=range(1)).T.reset_index()
        fi.columns = ['VARIABLE', 'TOTAL GAIN']
        fi = fi.sort_values('TOTAL GAIN', ascending=False)
        fi['IMPORTANCE'] = fi['TOTAL GAIN']**(0.5) / fi['TOTAL GAIN'].max()**(0.5) * 100
        fi['CONTRIBUTION'] = fi.IMPORTANCE/fi.IMPORTANCE.sum()
        return fi.reset_index(drop=True)

    c1, c2 = st.columns(2)

    c1.markdown('''##### Performance Metrics''')
    train_metrics = get_performance_metrics(train, train_dm)
    test_metrics = get_performance_metrics(test, test_dm,'TEST')
    combined_metrics = train_metrics.append(test_metrics)
    c1.dataframe(combined_metrics)
    gini_drop = (test_metrics['GINI']/train_metrics['GINI'] - 1).values[0]
    c2.title(f'{gini_drop*100:.2f}%')
    c2.write('GINI Change from Train to OOT')

    c1.markdown('''##### Variable Importance''')
    c1.dataframe(variable_importance(model))

    scoring = main_scoring.copy()
    scoring_dm = xgb.DMatrix(scoring[variables])

    scoring = scoring[variables + ['ticker']]
    scoring['predictions'] = model.predict(scoring_dm)
    scored = scoring.sort_values('predictions', ascending=False)
    st.markdown('''
    ---
    ##### Scoring on latest data (sample)
    ''')
    st.dataframe(scored.sample(5))

    st.markdown('''
    ##### Suggested Stocks TOP 5
    ''')
    suggested = scored.groupby('ticker').mean()['predictions'].reset_index()
    suggested = suggested.sort_values('predictions', ascending=False).head(5).reset_index(drop=True)
    st.dataframe(suggested)