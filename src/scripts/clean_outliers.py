import read_write as io
import datetime
import numpy as np
import pandas as pd
<< << << < HEAD


def df_qunatil(df):
    '''
    Filter period and percentiles
    '''
    df['period_m'] = pd.to_datetime(df['timestamps_UTC']).dt.strftime('%Y%m')
    df = df[df['period_m'] >= '2023-04-01']
    cols_use = set(df.columns) - {'Unnamed: 0',
                                  'mapped_veh_id',
                                  'timestamps_UTC',
                                  'lat',
                                  'lon',
                                  'period'}
    dfQuantil = df[list(cols_use)].describe(percentiles=[0.05, .25, .75, 0.9])
    return dfQuantil


def df_treeshold(df):
    '''
    Allows to have the upper whisker of a boxplot
    '''
    q5 = df.loc[['5%']].values.flatten().tolist()
    q25 = df.loc[['25%']].values.flatten().tolist()
    q75 = df.loc[['75%']].values.flatten().tolist()
    q90 = df.loc[['90%']].values.flatten().tolist()
    lim_inf = [w - 1.5 * (y - x) for w, x, y, z in zip(q5, q25, q75, q90)]
    lim_sup = [z + 1.5 * (y - x) for w, x, y, z in zip(q5, q25, q75, q90)]
    df.loc['lim_inf'] = lim_inf
    df.loc['lim_sup'] = lim_sup
    limit_airTemp = df.loc[['lim_sup']].RS_E_InAirTemp_PC1.values[0]
    limit_rpm = df.loc[['lim_sup']].RS_E_RPM_PC1.values[0]
    limit_waterT = df.loc[['lim_sup']].RS_E_WatTemp_PC1.values[0]
    limit_oilT = df.loc[['lim_sup']].RS_T_OilTemp_PC1.values[0]
    limit_oilP = df.loc[['lim_sup']].RS_E_OilPress_PC1.values[0]
    return limit_airTemp, limit_rpm, limit_waterT, limit_oilT, limit_oilP


def change_outliers(df,
                    limit_airTemp,
                    limit_rpm,
                    limit_waterT,
                    limit_oilT,
                    limit_oilP):
    '''change the outliers for the median'''
    df['period_m'] = pd.to_datetime(
        df['timestamps_UTC']).dt.strftime('%Y%m').astype(int)
    dfMedian = df[df['period_m'] >= 202304]

    median_Airtemp = dfMedian['RS_E_InAirTemp_PC1'].median()
    median_RPM = dfMedian['RS_E_RPM_PC1'].median()
    median_Watertemp = dfMedian['RS_E_WatTemp_PC1'].median()
    median_Oiltemp = dfMedian['RS_T_OilTemp_PC1'].median()
    median_OilPres = dfMedian['RS_E_OilPress_PC1'].median()

    df['RS_E_InAirTemp_PC1'] = np.where(
        df['RS_E_InAirTemp_PC1'] <= limit_airTemp,
        df['RS_E_InAirTemp_PC1'], median_Airtemp)
    df['RS_E_InAirTemp_PC2'] = np.where(
        df['RS_E_InAirTemp_PC2'] <= limit_airTemp,
        df['RS_E_InAirTemp_PC2'], median_Airtemp)
    df['RS_E_RPM_PC1'] = np.where(
        df['RS_E_RPM_PC1'] <= limit_rpm,
        df['RS_E_RPM_PC1'], median_RPM)
    df['RS_E_RPM_PC2'] = np.where(
        df['RS_E_RPM_PC2'] <= limit_rpm,
        df['RS_E_RPM_PC2'], median_RPM)
    df['RS_E_WatTemp_PC1'] = np.where(
        df['RS_E_WatTemp_PC1'] <= limit_waterT,
        df['RS_E_WatTemp_PC1'], median_Watertemp)
    df['RS_E_WatTemp_PC2'] = np.where(
        df['RS_E_WatTemp_PC2'] <= limit_waterT,
        df['RS_E_WatTemp_PC2'], median_Watertemp)
    df['RS_T_OilTemp_PC1'] = np.where(
        df['RS_T_OilTemp_PC1'] <= limit_oilT,
        df['RS_T_OilTemp_PC1'], median_Oiltemp)
    df['RS_T_OilTemp_PC2'] = np.where(
        df['RS_E_InAirTemp_PC2'] <= limit_oilT,
        df['RS_E_InAirTemp_PC2'], median_Oiltemp)
    df['RS_E_OilPress_PC1'] = np.where(
        df['RS_E_OilPress_PC1'] <= limit_oilP,
        df['RS_E_OilPress_PC1'], median_OilPres)
    df['RS_E_OilPress_PC2'] = np.where(
        df['RS_E_OilPress_PC2'] <= limit_oilP,
        df['RS_E_OilPress_PC2'], median_OilPres)
    return df


def main():
    dfIni = io.read_data(io.Filenames.original_data, parquet=False)
    dfQuantil = df_qunatil(dfIni)
    limit_airTemp, limit_rpm, limit_waterT, limit_oilT, limit_oilP = df_treeshold(
        dfQuantil)
    df = change_outliers(dfIni,
                         limit_airTemp,
                         limit_rpm,
                         limit_waterT,
                         limit_oilT,
                         limit_oilP)


== == == =


def df_treshold(df):
    '''
    Allows to have the upper and lower whisker of a boxplot
    '''
    df['period'] = df['timestamps_UTC'].str[:10]
    df['period_m'] = df['period'].str[:7]
    df['period_m'] = df['period_m'].str[:4].astype(
        int) * 100 + df['period_m'].str[6:7].astype(int)
    df = df[df['period_m'] >= 202304]
    cols_use = set(df.columns) - {'Unnamed: 0',
                                  'mapped_veh_id',
                                  'timestamps_UTC',
                                  'lat',
                                  'lon',
                                  'period'}
    dfQuantil = df[list(cols_use)].describe(percentiles=[0.05, .25, .75, 0.9])
    q5 = dfQuantil.loc[['5%']].values.flatten().tolist()
    q25 = dfQuantil.loc[['25%']].values.flatten().tolist()
    q75 = dfQuantil.loc[['75%']].values.flatten().tolist()
    q90 = dfQuantil.loc[['90%']].values.flatten().tolist()
    lim_inf = [w - 1.5 * (y - x) for w, x, y, z in zip(q5, q25, q75, q90)]
    lim_sup = [z + 1.5 * (y - x) for w, x, y, z in zip(q5, q25, q75, q90)]
    dfQuantil.loc['lim_inf'] = lim_inf
    dfQuantil.loc['lim_sup'] = lim_sup
    return dfQuantil.loc[['lim_inf',
                          'lim_sup'],
                         ['RS_E_InAirTemp_PC1',
                          'RS_E_RPM_PC1',
                          'RS_E_WatTemp_PC1',
                          'RS_T_OilTemp_PC1',
                          'RS_E_OilPress_PC1']]


def limit_table_sup(
        df,
        limit_airTemp,
        limit_rpm,
        limit_waterT,
        limit_oilT,
        limit_oilP):
    '''
    Detect how many upper outilers we have per day and vehicule
    '''
    df['period'] = df['timestamps_UTC'].str[:10]
    df['period_m'] = df['period'].str[:7]
    dfAgg = df.groupby(['period', 'mapped_veh_id'], as_index=False)\
        .agg(
            RS_E_InAirTemp_PC1=('RS_E_InAirTemp_PC1', lambda x: (x >= limit_airTemp).sum()),
            RS_E_InAirTemp_PC2=('RS_E_InAirTemp_PC2', lambda x: (x >= limit_airTemp).sum()),
            RS_E_RPM_PC1=('RS_E_RPM_PC1', lambda x: (x >= limit_rpm).sum()),
            RS_E_RPM_PC2=('RS_E_RPM_PC2', lambda x: (x >= limit_rpm).sum()),
            RS_E_WatTemp_PC1=('RS_E_WatTemp_PC1', lambda x: (x >= limit_waterT).sum()),
            RS_E_WatTemp_PC2=('RS_E_WatTemp_PC2', lambda x: (x >= limit_waterT).sum()),
            RS_T_OilTemp_PC1=('RS_T_OilTemp_PC1', lambda x: (x >= limit_oilT).sum()),
            RS_T_OilTemp_PC2=('RS_T_OilTemp_PC2', lambda x: (x >= limit_oilT).sum()),
            RS_E_OilPress_PC1=('RS_E_OilPress_PC1', lambda x: (x >= limit_oilP).sum()),
            RS_E_OilPress_PC2=('RS_E_OilPress_PC2', lambda x: (x >= limit_oilP).sum())
    )
    cond_1 = (dfAgg['RS_E_InAirTemp_PC1'] > 1)
    cond_2 = (dfAgg['RS_E_InAirTemp_PC2'] > 1)
    cond_3 = (dfAgg['RS_E_RPM_PC1'] > 1)
    cond_4 = (dfAgg['RS_E_RPM_PC2'] > 1)
    cond_5 = (dfAgg['RS_E_WatTemp_PC1'] > 1)
    cond_6 = (dfAgg['RS_E_WatTemp_PC2'] > 1)
    cond_7 = (dfAgg['RS_T_OilTemp_PC1'] > 1)
    cond_8 = (dfAgg['RS_T_OilTemp_PC2'] > 1)
    cond_9 = (dfAgg['RS_E_OilPress_PC1'] > 1)
    cond_10 = (dfAgg['RS_E_OilPress_PC2'] > 1)
    conditions = (cond_1 | cond_2 | cond_3 | cond_4 | cond_5 |
                  cond_6 | cond_7 | cond_8 | cond_9 | cond_10)
    dfAgg = dfAgg[conditions].reset_index(drop=True)
    return dfAgg


def main():
    df = io.read_data(io.Filenames.original_data, parquet=False)
    limits_table = df_treshold(df)
    limit_airTemp_sup = limits_table.loc[[
        'lim_sup']].RS_E_InAirTemp_PC1.values[0]
    limit_rpm_sup = limits_table.loc[['lim_sup']].RS_E_RPM_PC1.values[0]
    limit_waterT_sup = limits_table.loc[['lim_sup']].RS_E_WatTemp_PC1.values[0]
    limit_oilT_sup = limits_table.loc[['lim_sup']].RS_T_OilTemp_PC1.values[0]
    limit_oilP_sup = limits_table.loc[['lim_sup']].RS_E_OilPress_PC1.values[0]
    limit_airTemp_inf = 0
    limit_rpm_inf = 0
    limit_waterT_inf = 0
    limit_oilT_inf = 0
    limit_oilP_inf = 0
    df['RS_E_InAirTemp_PC1'] = np.where(
        df['RS_E_InAirTemp_PC1'].between(
            limit_airTemp_inf,
            limit_airTemp_sup),
        df['RS_E_InAirTemp_PC1'],
        df['RS_E_InAirTemp_PC1'].median())
    df['RS_E_InAirTemp_PC2'] = np.where(
        df['RS_E_InAirTemp_PC2'].between(
            limit_airTemp_inf,
            limit_airTemp_sup),
        df['RS_E_InAirTemp_PC2'],
        df['RS_E_InAirTemp_PC2'].median())
    df['RS_E_RPM_PC1'] = np.where(
        df['RS_E_RPM_PC1'].between(
            limit_rpm_inf,
            limit_rpm_sup),
        df['RS_E_RPM_PC1'],
        df['RS_E_RPM_PC1'].median())
    df['RS_E_RPM_PC2'] = np.where(
        df['RS_E_RPM_PC2'].between(
            limit_rpm_inf,
            limit_rpm_sup),
        df['RS_E_RPM_PC2'],
        df['RS_E_RPM_PC2'].median())
    df['RS_E_WatTemp_PC1'] = np.where(
        df['RS_E_WatTemp_PC1'].between(
            limit_waterT_inf,
            limit_waterT_sup),
        df['RS_E_WatTemp_PC1'],
        df['RS_E_WatTemp_PC1'].median())
    df['RS_E_WatTemp_PC2'] = np.where(
        df['RS_E_WatTemp_PC2'].between(
            limit_waterT_inf,
            limit_waterT_sup),
        df['RS_E_WatTemp_PC2'],
        df['RS_E_WatTemp_PC2'].median())
    df['RS_T_OilTemp_PC1'] = np.where(
        df['RS_T_OilTemp_PC1'].between(
            limit_oilT_inf,
            limit_oilT_sup),
        df['RS_T_OilTemp_PC1'],
        df['RS_T_OilTemp_PC1'].median())
    df['RS_T_OilTemp_PC2'] = np.where(
        df['RS_E_InAirTemp_PC2'].between(
            limit_oilT_inf,
            limit_oilT_sup),
        df['RS_E_InAirTemp_PC2'],
        df['RS_E_InAirTemp_PC2'].median())
    df['RS_E_OilPress_PC1'] = np.where(
        df['RS_E_OilPress_PC1'].between(
            limit_oilP_inf,
            limit_oilP_sup),
        df['RS_E_OilPress_PC1'],
        df['RS_E_OilPress_PC1'].median())
    df['RS_E_OilPress_PC2'] = np.where(
        df['RS_E_OilPress_PC2'].between(
            limit_oilP_inf,
            limit_oilP_sup),
        df['RS_E_OilPress_PC2'],
        df['RS_E_OilPress_PC2'].median())


>>>>>> > 7f10ff465bc3453e59a80b1e4c73cc0290c5e817
io.write_data(df, io.Filenames.data_cleaned)
return


if __name__ == "__main__":
    main()