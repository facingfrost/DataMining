import read_write
import pandas as pd


def clean_tfloat(data: pd.DataFrame) -> pd.DataFrame:
    '''Cleans the data for the floating point values

    returns a dataframe with the data cleaned     
    '''
    return data


def clean_position(data: pd.DataFrame) -> pd.DataFrame:
    '''Clean erroneus latitude and longitude

    returns a dataframe with the data cleaned
    '''
    return data


def clean():
    data = read_write.read_data(
        read_write.Filenames.data_with_weather.value)
    data = clean_tfloat(data)
    data = clean_position(data)
    read_write.write_data(data, read_write.Filenames.data_cleaned.value)


def main():
    clean()
    return


if __name__ == "__main__":
    main()
