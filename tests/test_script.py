import unittest

import pandas as pd

from src import script
import datetime


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        test_data = pd.DataFrame(
            {'_time': [datetime.date(2022, 12, 25), datetime.date(2022, 11, 25)]
                , '_value': [20, 30], 'driver': ['Driver 1', 'Driver 2']})
        test_data['_time'] = pd.to_datetime(test_data['_time'])
        self.generator = script.ReportGenerator(data=test_data, timeframes=['M'])

    def test_group_data(self):
        output = self.generator.group_data(freq='M', column='_value')
        self.assertIsNotNone(output)

    def test_generate_session_report(self):
        output = self.generator.generate_session_report()
        self.assertIsNotNone(output)

    def test_generate_consumption_report(self):
        output = self.generator.generate_consumption_report()
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()
