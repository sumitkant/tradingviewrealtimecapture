

def resample_data(df, resample, resolution):
    if resolution != resample:
        aggregations = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}
        resampled_df = df.resample(
            rule=resample + 'Min',        # timeframe
            on='datetime',                # Resampling column
            origin='1990-01-04 9:15:00',  # starting point of resampling
            closed='left',                # considers data at 9:45 1min candle
            label='left',                 # label using opening candle or closing candle (left for opening candle)
        ).agg(aggregations).dropna()
        resampled_df = resampled_df.reset_index()
        return resampled_df

