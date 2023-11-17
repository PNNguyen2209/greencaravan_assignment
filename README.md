# Data Aggregation Script

The purpose of this script is to read data from a CSV file,
perform aggregation, and write the output to CSV.

As of now, the script supports the creation of reports for the
following features: 
- Total number of charging sessions per driver, per month, and
for the whole year
- Total and average number of charging sessions for the total
fleet of drivers, per month, and for the whole year
- Total and average consumption in kWH per driver, per month,
and for the whole year
- Total and average consumption in kWH for the total fleet
of drivers, per month, and for the whole year

The output of the script is separated into two CSV files: 
`sessions.csv` and `consumption.csv`, which contain the
aggregated information for the number of charging sessions and
the consumption, respectively. The aggregation across
different time frames is supported and can be specified at
the creation of the `ReportGenerator` class. Aggregation
through different configurations can also be done by extending
the `ReportGenerator` class.