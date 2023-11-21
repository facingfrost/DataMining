import numpy as np
import pandas as pd
import datetime
import read_write as io

def check_conditions(row):
    '''Label target based on given conditions'''
    if row['track_or_stop'] == 0:
        condition_1 = (row['RS_E_InAirTemp_PC1'] > 65 or
                      row['RS_E_InAirTemp_PC2'] > 65 or
                      row['RS_E_WatTemp_PC1'] > 100 or
                      row['RS_E_WatTemp_PC2'] > 100 or
                      row['RS_T_OilTemp_PC1'] > 115 or
                      row['RS_T_OilTemp_PC2'] > 115)
        if condition_1:
            return 1
        else:
            return 0
    else:
        return None

def main():
    data = io.read_data(io.Filenames.data_with_weather)
    data['target'] = data.apply(lambda row: check_conditions(row), axis=1)
    data['period'] = pd.to_datetime(data['timestamps_UTC']).dt.strftime('%Y%m')
    io.write_data(data, io.Filenames.data_labeled)
    return

if __name__ == "__main__":
    main()

    