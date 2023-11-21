import numpy as np
import pandas as pd
import datetime
import read_write as io
from optbinning import OptimalBinning

def formatTablewoeiv(df, flagTotal = False):
  '''Formats the WoE table into a DF'''
  df = df.copy()
  df['Bin'] = df['Bin'].astype(str)
  df["row_num"]  = df.groupby(['VARIABLE']).cumcount()
  df["row_num"] = df["row_num"].astype(str).str.zfill(2)
  df['CLAVE'] = df['row_num'] + '.- ' + df['Bin']
  if flagTotal == True:
    df.loc[df['Bin'].fillna('') == '', ['Bin', 'CLAVE']] = ['Total', '99.- Total']
  else:
    df.loc[df['Bin'].fillna('') == '', 'Count'] = 0
  df = df[df['Count'] >0].reset_index(drop = True)
  return df

def woeiv_table(df, target, varNumeric, dictUserSplits):
  '''Generates a: \n
        dictOP:dictionary with index of range\n
        dictOB:dictionary with splits for each variable\n
        dfWOEIV: resume df formated  
  '''
  dictOP = {}
  dictOB = {}
  dfWOEIV = pd.DataFrame()
  dictOP_OOT = {}
  dictOB_OOT = {}
  dfWOEIV_OOT = pd.DataFrame()
  for col in varNumeric:
    # Train
    x = df[col].values
    y = df[target]
    optb = OptimalBinning(name = col, dtype = "numerical", solver = "cp", monotonic_trend = 'auto_asc_desc',
                          user_splits = dictUserSplits.get(col, None))
    optb.fit(x, y)

    dictOP[col] = optb.binning_table
    dictOB[col] = optb
        
    dfWOEIVAux = optb.binning_table.build()
    dfWOEIVAux['VARIABLE'] = col
    if not dfWOEIV.empty:
        dfWOEIV = dfWOEIV.loc[dfWOEIV['VARIABLE'] != col].reset_index(drop = True)
    dfWOEIV = pd.concat([dfWOEIV, dfWOEIVAux], ignore_index=True)
    dfWOEIV = formatTablewoeiv(dfWOEIV)
  return dictOP, dictOB, dfWOEIV

def varstouse(dfWOEIV, iv_min = 0.05):
    '''Returns and array with variables that have 5% information value or more,
      the param iv_min indicates the minimum iv allowed'''
    dfPlot = dfWOEIV.groupby('VARIABLE', as_index = False).agg({'IV':'sum'})
    varModel = list(dfPlot[dfPlot['IV']>iv_min].VARIABLE.values)
    return varModel

def transform_datawoe(df, dfWOEIV, dictOB, varModel, dictSpecialCodes={}):
    '''Returns a df with variables transformed with the sufix _WOE_OB'''
    for variable in varModel:
        df[variable + '_WOE_OB'] = dictOB[variable].transform(df[variable])
        try:
            valorNuloWOE = dfWOEIV.loc[ ( dfWOEIV['VARIABLE'] == variable ) & ( dfWOEIV['Bin'] == 'Missing' ), 'WoE'].values[0]
            df.loc[df[variable].isnull(), variable + '_WOE_OB'] = valorNuloWOE
        except:
            print(variable + ':No Nulls')
        try:
            valorEspecialWOE = dfWOEIV.loc[ ( dfWOEIV['VARIABLE'] == variable ) & ( dfWOEIV['Bin'] == 'Special' ), 'WoE'].values[0]
            df.loc[df[variable].isin(dictSpecialCodes[variable]), variable + '_WOE_OB'] = valorEspecialWOE
        except:
           print(variable + ': No speacial variables')
    return df

def main():
    df = io.read_data(io.Filenames.data_labeled)
    varNumeric = ['RS_E_InAirTemp_PC1',
                  'RS_E_InAirTemp_PC2',
                  'RS_E_OilPress_PC1',
                  'RS_E_OilPress_PC2',
                  'RS_E_RPM_PC1',
                  'RS_E_RPM_PC2',
                  'RS_E_WatTemp_PC1',
                  'RS_E_WatTemp_PC2',
                  'RS_T_OilTemp_PC1',
                  'RS_T_OilTemp_PC2',
                  'coco',
                  'dwpt',
                  'prcp',
                  'pres',
                  'rhum',
                  'temp',
                  'wdir',
                  'wpgt',
                  'wspd']
    # removed snow, tsun, 'track_or_stop',
    dictOP, dictOB, dfWOEIV = woeiv_table(df, 'target', varNumeric, {})
    varModel = varstouse(dfWOEIV, iv_min = 0.05)
    df_woe = transform_datawoe(df, dfWOEIV, dictOB, varModel, dictSpecialCodes={})
    io.write_data(df_woe, io.Filenames.data_transformed_woe)
    return

if __name__ == "__main__":
    main()