import numpy as np
import pandas as pd
import datetime
import read_write as io


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
    dfIni = io.read_data(io.Filenames.original_data)
    dfQuantil = df_qunatil(dfIni)
    limit_airTemp, limit_rpm, limit_waterT, limit_oilT, limit_oilP = df_treeshold(
        dfQuantil)
    df = change_outliers(dfIni,
                         limit_airTemp,
                         limit_rpm,
                         limit_waterT,
                         limit_oilT,
                         limit_oilP)
    io.write_data(df, io.Filenames.data_cleaned)
    return


if __name__ == "__main__":
    main()
