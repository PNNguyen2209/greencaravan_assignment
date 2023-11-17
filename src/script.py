from typing import Optional

import pandas as pd
import sys

import datetime

class ReportGenerator:
    """
    The purpose of this class is to generate aggregated reports of the data based on specific configuration and exports
    them to csv format.
    """

    def __init__(self, data, timeframes):
        self.data = data
        self.timeframes = timeframes
        self.format_dict = {'M': '%Y-%m', 'D': '%Y-%m-%d', 'Y': '%Y'}

    def group_data(self, freq: str, column: str, factors: Optional[list] = None) -> pd.DataFrame:
        """
        Aggregates data by a specific combination of factors and timeframe.
        :param freq: The frequency the data will be grouped by.
        :param column: The column that we apply operations to.
        :param factors: (Optional) list of factors.
        :return: Aggregated dataframe.
        """

        if factors is not None:
            df = (self.data.groupby(factors + [pd.Grouper(key='_time', axis=0, freq=freq)], axis=0)[column].sum()
                  .unstack().reset_index().fillna(0))
            df = df.transpose()
            df.columns = df.iloc[0]
            df = df[1:]
        else:
            df = (self.data.groupby(pd.Grouper(key='_time', axis=0, freq=freq))[column].sum().reset_index().fillna(0))
            df = df.set_index('_time')

        return df.apply(pd.to_numeric)  # Convert data back to numerical format.

    def generate_session_report(self) -> pd.DataFrame:
        """
        Generates a report of total and average numbers of charging sessions per driver and the entire fleet of drivers,
        aggregated over month and year.
        :return: Complete dataframe.
        """
        timeframe_dfs = []

        for timeframe in self.timeframes:
            # Group sessions per driver and timeframe.
            self.data['count'] = 1  # Generate a 1s column for counting.
            drivers = self.group_data(freq=timeframe, column='count', factors=['driver'])
            drivers = drivers.add_suffix(', total sessions')

            # Group sessions for all drivers per timeframe, average over number of drivers.
            self.data['Fleet'] = 1  # Generate a 1s column for counting.
            fleet = self.group_data(freq=timeframe, column='Fleet')
            fleet_avg = (fleet / self.data['driver'].unique().size).add_suffix(', avg sessions per driver')
            fleet.add_suffix(', total sessions')

            # Concatenate data frames and format time indexes.
            final = pd.concat([drivers, fleet, fleet_avg], axis=1)
            final.index = pd.to_datetime(final.index).strftime(self.format_dict.get(timeframe))

            timeframe_dfs.append(final)

        return pd.concat(timeframe_dfs)

    def generate_consumption_report(self) -> pd.DataFrame:
        """
        Generates a report of total and average consumption in kWH per driver and the entire fleet of drivers,
        aggregated over month and year.
        :return: Complete dataframe.
        """

        timeframe_dfs = []

        for timeframe in self.timeframes:
            # Group consumption per driver and timeframe, average over number of sessions.
            drivers = self.group_data(freq=timeframe, column='_value', factors=['driver'])
            self.data['count'] = 1  # Generate a 1s column for counting.
            drivers_sessions = self.group_data(freq=timeframe, column='count', factors=['driver'])
            drivers_avg = (drivers / drivers_sessions).fillna(0).add_suffix(', avg kWH per session')
            drivers = drivers.add_suffix(', total kWH')

            # Group consumption for all drivers per timeframe, average over number of sessions.
            fleet = self.group_data(freq=timeframe, column='_value').rename(columns={'_value': 'Fleet'})
            self.data['Fleet'] = 1  # Generate a 1s column for counting.
            fleet_sessions = self.group_data(freq=timeframe, column='Fleet')
            fleet_avg = (fleet / fleet_sessions).fillna(0).add_suffix(', avg kWH per session')
            fleet = fleet.add_suffix(', total kWH')

            # Concatenate data frames and format time indexes.
            final = pd.concat([drivers, drivers_avg, fleet, fleet_avg], axis=1)
            final.index = pd.to_datetime(final.index).strftime(self.format_dict.get(timeframe))

            timeframe_dfs.append(final)

        return pd.concat(timeframe_dfs)


def format_dataset(path: str) -> pd.DataFrame:
    """
    Formats the dataset by removing unnecessary rows and columns and sets the appropriate data types.
    :return: Pandas dataframe
    """

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        sys.exit('File could not be found')

    df.columns = df.iloc[2]
    df = df.drop(df.columns[range(0, 5)], axis=1).drop(range(0, 3), axis=0).reset_index(drop=True)

    df['_time'] = pd.to_datetime(df['_time'])
    df['_value'] = pd.to_numeric(df['_value'])

    return df


if __name__ == '__main__':
    data = format_dataset('../data/2022-01-14-17-00_influxdb_data.csv')
    generator = ReportGenerator(data, ['M', 'Y'])   # Timeframe can be adjusted.
    df = generator.generate_session_report().to_csv('reports/sessions.csv')
    df2 = generator.generate_consumption_report().to_csv('reports/consumption.csv')
