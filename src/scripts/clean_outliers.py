import numpy as np
import pandas as pd
import datetime
import read_write as io
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


def quantil_dataframe(df):
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


def df_threshold(df):
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

    df['RS_E_InAirTemp_PC1'] = np.where(
        df['RS_E_InAirTemp_PC1'] <= limit_airTemp,
        df['RS_E_InAirTemp_PC1'], np.nan)
    df['RS_E_InAirTemp_PC2'] = np.where(
        df['RS_E_InAirTemp_PC2'] <= limit_airTemp,
        df['RS_E_InAirTemp_PC2'], np.nan)
    df['RS_E_RPM_PC1'] = np.where(
        df['RS_E_RPM_PC1'] <= limit_rpm,
        df['RS_E_RPM_PC1'], np.nan)
    df['RS_E_RPM_PC2'] = np.where(
        df['RS_E_RPM_PC2'] <= limit_rpm,
        df['RS_E_RPM_PC2'], np.nan)
    df['RS_E_WatTemp_PC1'] = np.where(
        df['RS_E_WatTemp_PC1'] <= limit_waterT,
        df['RS_E_WatTemp_PC1'], np.nan)
    df['RS_E_WatTemp_PC2'] = np.where(
        df['RS_E_WatTemp_PC2'] <= limit_waterT,
        df['RS_E_WatTemp_PC2'], np.nan)
    df['RS_T_OilTemp_PC1'] = np.where(
        df['RS_T_OilTemp_PC1'] <= limit_oilT,
        df['RS_T_OilTemp_PC1'], np.nan)
    df['RS_T_OilTemp_PC2'] = np.where(
        df['RS_T_OilTemp_PC2'] <= limit_oilT,
        df['RS_T_OilTemp_PC2'], np.nan)
    df['RS_E_OilPress_PC1'] = np.where(
        df['RS_E_OilPress_PC1'] <= limit_oilP,
        df['RS_E_OilPress_PC1'], np.nan)
    df['RS_E_OilPress_PC2'] = np.where(
        df['RS_E_OilPress_PC2'] <= limit_oilP,
        df['RS_E_OilPress_PC2'], np.nan)
    return df


def imp_transform(df):
    imp_mean = IterativeImputer(random_state=42, max_iter=10)
    df_train = df.loc[:, ['RS_E_InAirTemp_PC1',
                          'RS_E_InAirTemp_PC2',
                          'RS_E_OilPress_PC1',
                          'RS_E_OilPress_PC2',
                          'RS_E_RPM_PC1',
                          'RS_E_RPM_PC2',
                          'RS_E_WatTemp_PC1',
                          'RS_E_WatTemp_PC2',
                          'RS_T_OilTemp_PC1',
                          'RS_T_OilTemp_PC2']]
    imp_mean.fit(df_train)
    df_imp = imp_mean.transform(df_train)
    df.loc[:, ['RS_E_InAirTemp_PC1',
               'RS_E_InAirTemp_PC2',
               'RS_E_OilPress_PC1',
               'RS_E_OilPress_PC2',
               'RS_E_RPM_PC1',
               'RS_E_RPM_PC2',
               'RS_E_WatTemp_PC1',
               'RS_E_WatTemp_PC2',
               'RS_T_OilTemp_PC1',
               'RS_T_OilTemp_PC2']] = df_imp
    return df


def main():
    df = io.read_data(io.Filenames.data_cleaned)
    dfQuantil = quantil_dataframe(df)
    limit_airTemp, limit_rpm, limit_waterT, limit_oilT, limit_oilP = df_threshold(
        dfQuantil)
    df = change_outliers(df,
                         limit_airTemp,
                         limit_rpm,
                         limit_waterT,
                         limit_oilT,
                         limit_oilP)
    df = imp_transform(df)
    df.drop(['period_m'], axis=1, inplace=True)
    io.write_data(df, io.Filenames.outliers_fixed)
    return


if __name__ == "__main__":
    main()
