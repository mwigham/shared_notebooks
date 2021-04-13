import pandas as pd
import numpy as np

"""This class contains functions for doing basic statistical analysis on a data frame in pandas"""

class DataframeAnalyser():

    PANDAS_AVERAGE = "mean"
    PANDAS_SUM = "sum"
    PANDAS_COUNT = "count"
    PANDAS_FIRST = "first"

    def __init__(self, dataframe):
        self.dataframe= dataframe

        ## TODO: add initialisation from csv, dicts etc.

    def countRowsInDataframe(self):
        """Counts how many rows there are in the data frame"""
        return len(self.dataframe.index)

    def getColumnTotal(self, columnName):
        """Adds up the values in a column"""
        return sum(self.dataframe[columnName])

    def getColumnCount(self, columnName, columnValue=None):
        """Counts values in a column, optionally only those equal to a certain value"""
        if columnValue:
            return len(self.dataframe[self.dataframe[columnName] == columnValue].index)
        return len(list(self.dataframe[columnName]))

    def pivotDataFrame(self, indexColumns, valueColumns, aggregationFunction):
        """Pivots the data frame using the indexcolumn or columns as identifiers. Value columns are aggregated using the
        aggregation function
        returns the pivoted data frame
        """
        if isinstance(aggregationFunction, dict) or isinstance(aggregationFunction, list):
            aggFunc = aggregationFunction
        elif isinstance(aggregationFunction, str):
            aggFunc = [aggregationFunction]
        else:
            raise ValueError("Don't know how to handle aggregation function %s"%aggregationFunction
                             )
        pivoted_frame =  pd.pivot_table(self.dataframe, values=valueColumns, index=indexColumns, aggfunc=aggFunc)
        pivoted_frame = pivoted_frame.reset_index()
        return pivoted_frame

    def calculateStatisticsPerColumnValue(self, columnName, valueColumns, statistic, excludeZeros=False, sortColumn=None):
        """Calculates the specified statistic for each of the value columns, for each
        value in columnName. E.g. if columnName is the name of a person, and valueColumns of the
        times that person appeared onscreen or spoke, then for each person the statistic
        will be calculated for onscreen time and speaking time
        if excludeZeros is true, then zero values in the value columns will be excluded from the calculation
        sortColumn is an optional column on which the results should be sorted
        Returns a list of the column values, and a list of lists of the corresponding statistics
        """
        values = []
        values.extend(valueColumns)
        values.append(columnName)

        if sortColumn and sortColumn not in valueColumns:
            values.append(sortColumn)
        column_values_statistics = self.dataframe[values]

        if excludeZeros:  # if excluding zeros, replace the 0s with NaN. They are then automatically excluded
            column_values_statistics = column_values_statistics.replace(0, np.NaN)

        statistics = pd.pivot_table(column_values_statistics, values=valueColumns, index=columnName, aggfunc=[statistic])

        statistics.columns = statistics.columns.droplevel(0)

        if sortColumn:
            statistics = statistics.reindex(statistics[sortColumn].sort_values(ascending=False).index)

        output_statistics = []
        for column in valueColumns:
            output_statistics.append(list(statistics[column]))

        return list(statistics.index.values), output_statistics


    def calculateTotalsPerColumnValue(self, columnName, valueColumns, excludeZeros=False, sortColumn=None):
        """Calculates the total for each of the value columns, for each
        value in columnName. E.g. if columnName is the name of a person, and valueColumns of the
        times that person appeared onscreen or spoke, then for each person the total onscreen time and
        total speaking time will be calculated
        if excludeZeros is true, then zero values in the value columns will be excluded from the calculation
        sortColumn is an optional column on which the results should be sorted
        Returns a list of the column values, and a list of lists of the corresponding totals
        """
        return self.calculateStatisticsPerColumnValue(columnName, valueColumns, self.PANDAS_SUM, excludeZeros, sortColumn)

    def calculateAveragesPerColumnValue(self, columnName, valueColumns, excludeZeros=False, sortColumn=None):
        """Calculates the average for each of the value columns, for each
        value in columnName. E.g. if columnName is the name of a person, and valueColumns of the
        times that person appeared onscreen or spoke, then for each person the total onscreen time and
        total speaking time will be calculated
        if excludeZeros is true, then zero values in the value columns will be excluded from the calculation
        sortColumn is an optional column on which the results should be sorted
        Returns a list of the column values, and a list of lists of the corresponding totals
        """

        return self.calculateStatisticsPerColumnValue(columnName, valueColumns, self.PANDAS_AVERAGE, excludeZeros, sortColumn)

