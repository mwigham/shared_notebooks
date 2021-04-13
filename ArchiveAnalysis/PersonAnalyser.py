from ArchiveAnalysis.DataframeAnalyser import DataframeAnalyser
import pandas as pd

"""This class accepts a pandas dataframe with data about the appearances of persons in a set of programmes. It
can then perform various statistical calculations, such as the most frequently occurring persons, the average length of appearance
etc. If there are columns with additional characteristics of the person, such as their gender or political party, then 
statistics over these can also be produced, e.g. which gender appears most frequently

The dataframe should contain a row per appearance of a person in a programme. The minimum content is
a column for the name of the person, and a column for the date. 

Optional additional columns could be e.g.:
- programme name
- type of programme
- gender of person
- time person appeared onscreen
- time person spoke for
- total time person was visible/audible
"""

class PersonAnalyser(DataframeAnalyser):

    def countAppearancesPerColumnValue(self, columnName, dateColumnName, sortColumn=None):
        """Counts the appearances per value in the given column. E.g. to count the appearances per person, use the
        column containing the person's name.
        Returns a list of the column values, and a list of the corresponding counts, sorted in descending order"""

        appearances_dates = self.dataframe[[columnName, dateColumnName]]
        appearance_counts = pd.pivot_table(appearances_dates, values=[dateColumnName], index=columnName,
                                           aggfunc=[self.PANDAS_COUNT])
        appearance_counts.columns = appearance_counts.columns.droplevel(0)

        if sortColumn:
            appearance_counts = appearance_counts.reindex(appearance_counts[sortColumn].sort_values(ascending=False).index)

        return list(appearance_counts.index.values), list(appearance_counts[dateColumnName])


    def calculateTimeBreakdownPerColumnValue(self, columnName, timeColumns, sortColumn=None):
        """Calculates the totals of each time column per value in columnName. E.g. to get the total speaking time
        and total onscreen time per person, columnsToTotal would be the columns with those times, and columnName would
        be the column containing the person's name.
        sortColumn is an optional column on which the breakdowns are sorted. E.g. this could be the total time
        Returns a list of the column values, and a list of lists of the corresponding totals
        """

        values = []
        values.extend(timeColumns)
        if sortColumn and sortColumn not in timeColumns:
            values.append(sortColumn)

        appearances_times = self.dataframe[values + [columnName]]

        appearances_times_totals = pd.pivot_table(appearances_times,
                                                  values=values, index=columnName,
                                                  aggfunc=[self.PANDAS_SUM])

        appearances_times_totals.columns = appearances_times_totals.columns.droplevel(0)

        if sortColumn:
            appearances_times_totals = appearances_times_totals.reindex(
            appearances_times_totals[sortColumn].sort_values(ascending=False).index)

        output_totals = []

        for column in timeColumns:
            output_totals.append(list(appearances_times_totals[column]))

        return list(appearances_times_totals.index.values), output_totals


    def countProgrammeBroadcasts(self, programmeColumn, dateColumn):
        """Counts the number of broadcasts per programme"""

        programme_counts = pd.pivot_table(self.dataframe, index=[programmeColumn, dateColumn],
                                           aggfunc=[self.PANDAS_COUNT])

        programme_counts = pd.pivot_table(programme_counts, index=[programmeColumn],
                                           aggfunc=[self.PANDAS_COUNT])
        programme_counts.columns = programme_counts.columns.droplevel(0)
        programme_counts = programme_counts.reset_index()

        return list(programme_counts[programmeColumn]), list(programme_counts[self.PANDAS_COUNT]["Name"])


    def calculateAverageTimePerColumnValue(self, columnName, timeColumns, excludeZeros=False, sortColumn=None):
        """Calculates the averages of the times in the time columns, for each value in the column columnName.
        E.g. if columnName contains the names of the persons, then the average of each time will be calculated
        per person"""

        return self.calculateAveragesPerColumnValue(columnName, timeColumns, excludeZeros, sortColumn)


    def calculateTotalTimePerColumnValue(self, columnName, timeColumns, excludeZeros=False, sortColumn=None):
        """Calculates the totals of the times in the time columns, for each value in the column columnName.
        E.g. if columnName contains the names of the persons, then the average of each time will be calculated
        per person"""

        return self.calculateTotalsPerColumnValue(columnName, timeColumns, excludeZeros, sortColumn)
