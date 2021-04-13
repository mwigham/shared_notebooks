import collections
import os
import plotly.io as pio
import chart_studio
from chart_studio import plotly as py
import plotly.graph_objects as go
import plotly.figure_factory as ff
from chart_studio.plotly import image as PlotlyImage
from PIL import Image as PILImage
import io
from Visualisation import NISVHouseStyle


class PlotlyViz:
	"""A class for carrying out Plotly visualisations (e.g. in a Jupyter notebook)
	Works in either online mode (writes plots to the website) or offline (shows plots in the notebook)"""

	def __init__(self, mode, config = {}, saveAsFile= False, saveInFormat = [], saveInFolder = None):
		"""Initialises the PlotlyViz class in online or offline mode. In online mode, plots are written to the Plotly
		website under the user account. In offline mode, they are either plotted in a notebook of saved to HTML
		For online mode, a config with a valid Plotly username and apiKey is necessary.
		For offline mode, no config is needed. You can optionally set saveAsFile to True, then instead of viewing graphs
		in a Jupyter Notebook, they will be saved as files. You must then specify a list with the format(s) you want to save
		the graph in: "html" for interactive html files,
		"png" for static PNG, "jpg" for static JPEG."""

		self.__MODE = mode
		self.__saveAsFile = saveAsFile
		self.__saveInFormat = saveInFormat
		self.__saveInFolder = saveInFolder

		self.__ONLINE = "ONLINE"
		self.__OFFLINE = "OFFLINE"

		if self.__MODE == self.__ONLINE:
			if not config or "USERNAME" not in config or "API_KEY" not in config:
				raise ValueError("For online mode you must enter a username and api key in the config")
			chart_studio.tools.set_credentials_file(username=config["USERNAME"], api_key=config["API_KEY"])
		elif self.__MODE == self.__OFFLINE:
			pass  # don't need to do anything
		else:
			raise ValueError("Invalid mode: " + str(self.__MODE))
            
		if not isinstance(self.__saveInFormat, list):
			raise ValueError("Formats must be given in a list")

	def __plotGraph(self, fig, filename, config=None):
		"""Plots the graph either in the notebook itself or to a HTML file (in offline mode)  or to the
		Plotly website (in online mode)
		In offline mode, you can also supply a config file to finetune how the graph is displayed, for example to hide
		the 'Export to Plotly' link
		Returns no values
		"""

		if self.__MODE == self.__ONLINE:
			py.plotly.plot(fig, filename=filename, auto_open=False)
		elif self.__MODE == self.__OFFLINE:
			if self.__saveAsFile:	
				for fileFormat in self.__saveInFormat: 
					if fileFormat not in ["html", "png", "jpg"]:
						raise ValueError("Invalid file format, must be one or more of \"html\", \"png\", \"jpg\"")
					if self.__saveInFolder:
						if filename.endswith(fileFormat):
							saveFilename = self.__saveInFolder + os.sep + filename
						else:
							saveFilename = self.__saveInFolder + os.sep + filename + "." + fileFormat
					else:
						if filename.endswith(fileFormat):
							saveFilename = filename
						else:
							saveFilename = filename + "." + fileFormat
					if fileFormat == "html":                                       
						pio.write_html(fig, saveFilename, auto_open=False, config=config)  # write it to a file
					else:
						img_bytes = PlotlyImage.get(fig)
						image = PILImage.open(io.BytesIO(img_bytes))
						image.save(saveFilename)
			else:
				pio.show(fig, filename=filename, config=config)
		else:
			raise ValueError("Unknown mode %s, should be %s or %s"%(self.__MODE, self.__ONLINE, self.__OFFLINE) )
			
	def combineRemainingSegmentsIntoOtherCategory(self, pieSegments, numberOfValuesToShow):
		"""Given a dictionary of pie segments (key is segment label, value is segment value), keeps the top
		numberOfValuesToShow segments, and combines the remaining ones
		into one category- "other", which is appended as an additional segment (dictionary entry).
		Returns the new dictionary of pie segments, and a dictionary of the categories that have been merged
		into "other".
		If the dictionary already contains the key "other" because this value is present in the metadata, then this
		will be a separate segment if it falls within the top numberOfValuesToShow segments. If not then it will added
		up with the remaining categories and be merged into 'other'"""

		output = collections.OrderedDict()  # save the top segments to be shown

		for key in list(pieSegments.keys())[:numberOfValuesToShow]:
			output[key] = pieSegments[key]

		# now combine the remaining segments into one category 'Other'
		otherDict = collections.OrderedDict()
		
		otherCount = 0
		for key, value in list(pieSegments.items())[numberOfValuesToShow:]:
			otherDict[key] = value
			otherCount += value
			
		if otherCount > 0: 
			output["OTHER"] = otherCount
		
		return output, otherDict

	def createTopXKeyValuesFigure(self, countDictionary, number, plotTitle, xTitle, yTitle, margin, colour = NISVHouseStyle.ROYAL_BLUE):
		"""Creates a figure showing the top 'number' largest values from the dictionary against their keys.
		Given a dictionary, this function sorts the dictionary in descending order of the values, and creates a bar
		chart of the first 'number' values against the keys.  The figure is given the defined title and x and y axis
		titles.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping the graph). See plotly documentation for more information
		Returns a Plotly figure as a dictionary
		"""
		
		sorted_keys = []
		sorted_values = []

		# sort the values in descending order, so we have the biggest first
		sorted_items = [(k, countDictionary[k]) for k in sorted(countDictionary, key=countDictionary.get, reverse=True)]

		for key, value in sorted_items:
			sorted_keys.append(key)
			sorted_values.append(value)

		# select the data for the 'number' biggest for plotting
		data = [go.Bar(
				x=sorted_keys[: number],
				y=sorted_values[: number],
				text=self.formatOverlayHoverInfo(sorted_keys[: number], sorted_values[: number], ""),
				hoverinfo='text',
				marker=dict(
					color=colour,
					line=dict(
						color=colour,
						width=2,
					)
					)
					)]


		# set up the chart
		layout = go.Layout(
			title=plotTitle,
			margin=margin,
			xaxis=dict(
				title=xTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			),
			yaxis=dict(
				title= yTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			), 
			separators=NISVHouseStyle.getSeparators()
		)
		
		# plot
		fig = go.Figure(data=data, layout=layout)
		
		return fig

	def plotTopXKeyValues(self, countDictionary, number, plotTitle, xTitle, yTitle, margin, filename, colour=NISVHouseStyle.ROYAL_BLUE):
		"""Plots the top 'number' largest values from the dictionary against their keys.
		Given a dictionary, this function sorts the dictionary in descending order of the values, and plots a bar chart
		of the first 'number' values against the keys.  The plot is given the defined title and x and y axis titles, and
		is plotted under the given filename.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""
		
		fig = self.createTopXKeyValuesFigure(countDictionary, number, plotTitle, xTitle, yTitle, margin, colour)
		
		self.__plotGraph(fig, filename)

	def createMultipleVariablesOverTimeAsLineGraphsFigure(self, variableValues, labels, timelines, plotTitle, xAxisTitle, yAxisTitle, margin,colours=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC], width=600, height=500):
		"""Creates a figure with each variable over time as a line.  'variableValues' should be a list containing lists
		of each value over time, 'labels' a list with the name for each variable, timelines a list containing lists of
		the time values for each variable (it is not assumed that these are the same for all series.  The figure and
		axis titles must also be specified.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns a Plotly figure as a dictionary"""
		
		# check that we have the right number of labels and data series
		if len(labels) != len(variableValues) or len(labels) != len(timelines):
			raise ValueError("variableValues, labels and timelines should each have the same length - the number of variable to be plotted")

		data = []
		i = 0
				
		for variableValue in variableValues:  # add each variable value as a line, with its label
			trace = go.Scatter(
						
						x=timelines[i], 
						y=variableValue, 
						text=self.formatOverlayHoverInfo(timelines[i], variableValue, labels[i]),
						hoverinfo='text',
						mode='lines', 
						name=labels[i],
						marker=dict(
							size=10,
							color=colours[i],
							line=dict(
								width=2
							)
						))
			data.append(trace)
			i += 1

		# set the titles
		layout = go.Layout(
			title=plotTitle,
			margin=margin,
			width=width,
			height=height,
			xaxis=dict(
				title=xAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			),
			yaxis=dict(
				title=yAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			), 
			separators=NISVHouseStyle.getSeparators()
		)
		fig = go.Figure(data=data, layout=layout)
		
		return fig

	def plotMultipleVariablesOverTimeAsLineGraphs(self, variableValues, labels, timelines, plotTitle, xAxisTitle, yAxisTitle, margin,filename, colours = [NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC], width=600, height=500):
		"""Plots each variable over time as a line.  'variableValues' should be a list containing lists of each value
		over time,'labels' a list with the label for each variable, timelines a list containing lists of the time values
		for each variable (it is not assumed that these are the same for all series.  The plot and axis titles must
		also be specified.  The plot is plotted under the given filename
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createMultipleVariablesOverTimeAsLineGraphsFigure(variableValues, labels, timelines, plotTitle, xAxisTitle, yAxisTitle, margin,colours, width, height)
		
		self.__plotGraph(fig, filename)
		
	def createYAgainstXAsBarChartFigure(self, x_axis, y_axis, plotTitle, xAxisTitle, yAxisTitle, margin, colour = NISVHouseStyle.ROYAL_BLUE, width = 600, height=500):
		"""Creates a figure with the Y axis values against the X axis values, using the specified titles in the plot and
		on the axes.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns a Plotly figure in a dictionary
		"""
		
		if not x_axis:
			raise ValueError("x_axis values list is empty")
			
		if not y_axis:
			raise ValueError("y_axis values list is empty")
			
		if len(x_axis) != len(y_axis):
			raise ValueError("The x and y axis values do not have the same number of values (%d and %d)"%(len(x_axis), len(y_axis)))

		data = [go.Bar(
					x=x_axis,
					y=y_axis,
					text=self.formatOverlayHoverInfo(x_axis, y_axis, ""),
					hoverinfo='text',
					marker=dict(
						color=colour,
						line=dict(
							color=colour,
							width=2,
						)
					)
					)]

		layout = go.Layout(
			title=plotTitle,
			width=width,
			height=height,
			margin=margin,
			xaxis=dict(
				title=xAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				),
					type="category"
			),
			yaxis=dict(
				title=yAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			)
			, 
			separators=NISVHouseStyle.getSeparators()
		)
		fig = go.Figure(data=data, layout=layout)    
			
		return fig 

	def plotYAgainstXAsBarChart(self, x_axis, y_axis, plotTitle, xAxisTitle, yAxisTitle, margin, filename, colour=NISVHouseStyle.ROYAL_BLUE, width=600, height=500):
		"""Plots the Y axis values against the X axis values, using the specified titles in the plot and on the axes,
		and is plotted under the given filename
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""
		
		fig = self.createYAgainstXAsBarChartFigure(x_axis, y_axis, plotTitle, xAxisTitle, yAxisTitle, margin, colour, width, height) 
			
		self.__plotGraph(fig, filename)  
	
	def createMultipleYsAgainstXAsBarChartFigure(self, x_axis, y_axisList, traceLabels, plotTitle, xAxisTitle, yAxisTitle, margin, colours=[NISVHouseStyle.ROYAL_BLUE, NISVHouseStyle.PINK, NISVHouseStyle.GREY, NISVHouseStyle.YELLOW], showRelativeValues = False):
		"""creates a figure with multiple Y traces against the X axis values, using the specified titles in the plot and
		on the axes.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns a Plotly figure as a dictionary
		"""
		
		if not x_axis:
			raise ValueError("x_axis values list is empty")
			
		if not y_axisList:
			raise ValueError("y_axis values list is empty")
			
		if len(colours) < len(y_axisList):
			raise ValueError("Too few colours specified, must specify at least as many colours as there are different Y sets")
			
		if len(traceLabels) != len(y_axisList):
			raise ValueError("Must have a label for each Y trace")
		
		for y_axis in y_axisList:
			if len(x_axis) != len(y_axis):
				raise ValueError("The x and y axis values do not have the same number of values")

		data = []
		
		i = 0
		for y_axis in y_axisList:
			trace = go.Bar(
					x=x_axis,
					y=y_axis,
					text=self.formatOverlayHoverInfo(x_axis, y_axis, traceLabels[i]),
					hoverinfo='text',
					name=traceLabels[i],
					marker=dict(
						color=colours[i],
						line=dict(
							color=colours[i],
							width=2,
						)
					)
					)
			data.append(trace)
			i += 1

		layout = go.Layout(
			title=plotTitle,
			margin=margin,
			xaxis=dict(
				title=xAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				),
				type="category"
			),
			yaxis=dict(
				title= yAxisTitle,
				titlefont=dict(
					family='Arial, monospace',
					size=18
				)
			), 
			separators=NISVHouseStyle.getSeparators()
		)
		fig = go.Figure(data=data, layout=layout)    
			
		return fig   

	def plotMultipleYsAgainstXAsBarChart(self, x_axis, y_axisList, traceLabels, plotTitle, xAxisTitle, yAxisTitle, margin, filename, colours=[NISVHouseStyle.ROYAL_BLUE, NISVHouseStyle.PINK, NISVHouseStyle.GREY, NISVHouseStyle.YELLOW], showRelativeValues=False):
		"""Plots multiple Y traces against the X axis values, using the specified titles in the plot and on the axes,
		and is plotted under the given filename
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createMultipleYsAgainstXAsBarChartFigure(x_axis, y_axisList, traceLabels, plotTitle, xAxisTitle, yAxisTitle, margin, colours, showRelativeValues)
			
		self.__plotGraph(fig, filename)

	def createStackedBarChartFigure(self, valuesLists, keysLists,  namesList, plotTitle, xAxisTitle, yAxisTitle, margin, colours):
		if len(valuesLists) != len(keysLists) != len(namesList):
			raise ValueError("Number of values, keys and names don't match")
		data = []
		i = 0
		for valuesList in valuesLists:
			data.append(go.Bar(
				x=keysLists[i],
				y=valuesList,
				text=self.formatOverlayHoverInfo(keysLists[i], valuesList,
												 namesList[i]),
				hoverinfo='text',
				name=namesList[i],
				marker=dict(color=colours[i])
			))
			i += 1

		layout = go.Layout(
			title=plotTitle,
			barmode='stack',
			xaxis=dict(
					title=xAxisTitle,
					titlefont=dict(family='Arial, monospace', size=18)
				),
			yaxis=dict(
			title=yAxisTitle,
			titlefont=dict(family='Arial, monospace', size=18)
			),
			margin=margin,
			separators = NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data=data, layout=layout)

		return fig

	def plotStackedBarChart(self, valuesLists, keysLists,  namesList, plotTitle, xAxisTitle, yAxisTitle, filename, margin, colours=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC]):
		fig = self.createStackedBarChartFigure(valuesLists, keysLists, namesList, plotTitle, xAxisTitle, yAxisTitle, margin,
									colours=colours)
		self.__plotGraph(fig, filename)

	def createOverlayBarChartFigureForTwoSetsItemsPerYear(self, firstSetItemsPerYear,secondSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameSecondSet, title, xAxisTitle, yAxisTitle, colours=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK], showRelativeValues=False):
		"""Creates an overlay bar chart of the second set of items per year, with stacked on this 
		the difference of the first set with the second set of items. The first set should have higher values than the
		second. The overall effect is to show the second set as one set of bars, with the difference between the sets on
		top, making it appear as if the second set is overlaid on the first.
		When the user hovers over the bars with the mouse, the value of the second set will be shown next to the name
		'nameSecondSet'	and the difference between the value of the first and second set will be shown next to the name
		'nameDifferenceFirstAndSecondSet.
		For example, if the first set contains all archive items, and the second set all items with speech recognition,
		then appropriate labels would be 'items without speech recognition' (for the difference) and
		'items with speech recognition' for the second set
		Expects that each itemsPerYear will be an ordered dictionary with the year string as key and the count of the
		items as the value.
		If the ranges of the years differ, the range of the first set is taken, and the 
		corresponding values looked up from the second set.  If they do not exist, a value of zero is assumed
		It is assumed that the first set has the largest values, so the second
		set is subtracted from this to create the chart.
				if showRelativeValues is true, then the bars will be normalised to show them as percentages.
		Returns a Ploty figure as a dictionary"""
		
		if not firstSetItemsPerYear:
			raise ValueError("There are no items for the first set")
			
		if not secondSetItemsPerYear:
			raise ValueError("There are no items for the second set")
			
		if not isinstance(firstSetItemsPerYear, type(collections.OrderedDict())) or not isinstance(secondSetItemsPerYear, type(collections.OrderedDict())):
			raise ValueError("Sets should be ordered dictionaries, with the year string as key, and the count as value")
		
		differenceValues = []
		selectedSecondSetValues = []  # to hold the selected second set values, as ranges could differ
		i = 0
		for year in firstSetItemsPerYear.keys():  # for each time interval in the range of the first set
			if year in secondSetItemsPerYear.keys():		 				
				differenceValues.append(firstSetItemsPerYear[year] - secondSetItemsPerYear[year])
				selectedSecondSetValues.append(secondSetItemsPerYear[year])
			else:  # raise error
				differenceValues.append(firstSetItemsPerYear[year])
				selectedSecondSetValues.append(0)
			i += 1
		
		if len(differenceValues) != len(selectedSecondSetValues) or len(differenceValues) !=len (firstSetItemsPerYear):
			raise ValueError("Couldn't create a cohesive set of values for the time range of the first set")
			
		if sum(differenceValues) < 0:
			raise ValueError("Second set values are larger than the first set")
			
		if showRelativeValues:  # scale all values to be percentages of the total
			i = 0
			for value in selectedSecondSetValues:
				sumValues = value + differenceValues[i]
				if sumValues != 0:
					selectedSecondSetValues[i] = (value/sumValues)*100
					differenceValues[i] = (differenceValues[i]/sumValues)*100
				i += 1
		
		data = [go.Bar(
				x=list(firstSetItemsPerYear.keys()),
				y=selectedSecondSetValues,
				text=self.formatOverlayHoverInfo(list(firstSetItemsPerYear.keys()), selectedSecondSetValues, nameSecondSet),
				hoverinfo='text',
				name=nameSecondSet,
				marker=dict(color=colours[0])
		),
				go.Bar(
				x=list(firstSetItemsPerYear.keys()),
				y=differenceValues,
				text=self.formatOverlayHoverInfo(list(firstSetItemsPerYear.keys()), differenceValues, nameDifferenceFirstAndSecondSet),
				hoverinfo='text',
				name=nameDifferenceFirstAndSecondSet,
				marker=dict(color=colours[1])
		)]

		layout = go.Layout(
			title=title,
			barmode='stack',
			xaxis=dict(
					title=xAxisTitle,
					titlefont=dict(family='Arial, monospace', size=18)
				),
			yaxis=dict(
			title=yAxisTitle,
			titlefont=dict(family='Arial, monospace', size=18)
			),
			separators = NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data=data, layout=layout)

		return fig

	def plotOverlayBarChartForTwoSetsItemsPerYear(self, firstSetItemsPerYear,secondSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameSecondSet, title, xAxisTitle, yAxisTitle, filename, colours = [NISVHouseStyle.BLUE, NISVHouseStyle.PINK], showRelativeValues = False):
		"""Plots the second set of items per year, with stacked on this the difference of the first set with the second
		set of items. The first set should have higher values than the second. The overall effect is to show the second
		set as one set of bars, with the difference between the sets on top, making it appear as if the second set is
		overlaid on the first.
		When the user hovers over the bars with the mouse, the value of the second set will be shown next to the name
		'nameSecondSet' and the difference between the value of the first and second set will be shown next to the name
		'nameDifferenceFirstAndSecondSet.
		For example, if the first set contains all archive items, and the second set all items with speech recognition,
		then appropriate
		labels would be 'items without speech recognition' (for the difference) and 'items with speech recognition' 
		Expects that each itemsPerYear will be an ordered dictionary with the year string as key and the count of the
		items as the value.
		If the ranges of the years differ, the range of the first set is taken, and the 
		corresponding values looked up from the second set.  If they do not exist, a value of zero is assumed..
		It is assumed that the first set has the largest values, so the second
		set is subtracted from this to create the chart.  Filename should not contain a suffix, that will be added
				if showRelativeValues is true, then the bars will be normalised to show them as percentages.
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
				"""

		fig = self.createOverlayBarChartFigureForTwoSetsItemsPerYear(firstSetItemsPerYear,secondSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameSecondSet, title, xAxisTitle, yAxisTitle, colours, showRelativeValues)

		self.__plotGraph(fig, filename)
		
		
	def formatOverlayHoverInfo(self, keys, values, name):
		"""Creates a list of hover infos for this part of the overlay graph. Hover information  has format
		'(key, value) name"""
		text = []
		i = 0
		for key in keys:
			text.append("(" + str(key) + ", " + NISVHouseStyle.formatNumber(values[i]) + ") " + name)
			i += 1
		return text

	def createOverlayBarChartFigureForThreeSetsItemsPerYear(self, firstSetItemsPerYear,secondSetItemsPerYear, thirdSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameDifferenceSecondAndThirdSet, nameThirdSet, title, xAxisTitle, yAxisTitle,colours = [NISVHouseStyle.GREEN, NISVHouseStyle.ORANGE, NISVHouseStyle.GREY], showRelativeValues = False):
		"""
		Creates a figure with the third set of items per year, with stacked on this the difference of the second set with
		the third set of items,	and stacked up on this the difference of the second set with the first set. The first
		set should have higher values than the second, and the second should have higher values than the third.
		The overall effect is to show the third set as one set of bars, with the difference between the sets on top,
		making it appear as if the third set is overlaid on the second, and the second set is overlaid on the first.
		When the user hovers over the bars with the mouse, the value of the third set will be shown next to the name
		'nameThirdSet',	the difference between the value of the first and second set will be shown next to the name
		nameDifferenceFirstAndSecondSet, and the difference between the value of the second and third set will be shown
		next to the name 'nameDifferenceSecondAndThirdSet'.
		For example, if the first set contains all archive items, and the second set all items for which speech
		recognition is possible, and the third all items already with speech recognition, then appropriate
		labels would be 'speech recognition impossible' (for the first/second difference),
		'waiting for speech recognition' (for the second/third difference) and 'speech recognition complete' (for the
		third set)
		Expects that each itemsPerYear will be an ordered dictionary, with the year string as key, and the count as value.
		If the ranges of the years differ, the range of the first set is taken, and the 
		corresponding values looked up from the second and third set.  If they do not exist, then a value of zero is assumed
		if showRelativeValues is true, then the bars will be normalised to show them as percentages.
		Returns a Plotly figure as a dictionary
	"""
		
		if not firstSetItemsPerYear:
			raise ValueError("There are no items for the first set")
			
		if not secondSetItemsPerYear:
			raise ValueError("There are no items for the second set")
			
		if not thirdSetItemsPerYear:
			raise ValueError("There are no items for the third set")
			
		if not isinstance(firstSetItemsPerYear, type(collections.OrderedDict())) or not isinstance(secondSetItemsPerYear, type(collections.OrderedDict())) or not isinstance(thirdSetItemsPerYear, type(collections.OrderedDict())):
			raise ValueError("Sets should be ordered dictionaries, with the year string as key, and the count as value")
		
		secondToFirstDifferenceValues = []
		thirdToSecondDifferenceValues = []
		selectedThirdSetValues = []  # to hold the selected third set values, as ranges could differ
		i = 0
		for year in firstSetItemsPerYear.keys():  # for each year in the first set
			if year in secondSetItemsPerYear.keys():
					secondToFirstDifferenceValues.append(firstSetItemsPerYear[year] - secondSetItemsPerYear[year])
					# now get the value from the third set
					if year in thirdSetItemsPerYear.keys():
						thirdToSecondDifferenceValues.append(secondSetItemsPerYear[year] - thirdSetItemsPerYear[year])
						selectedThirdSetValues.append(thirdSetItemsPerYear[year])
					else:  # assume zero
						thirdToSecondDifferenceValues.append(secondSetItemsPerYear[year])
						selectedThirdSetValues.append(0)
			else:  # raise error, as don't know how to interpret this
				raise ValueError("Year %s is missing in second set"%year)
			i += 1
		
		if len(secondToFirstDifferenceValues) != len(thirdToSecondDifferenceValues) or len(secondToFirstDifferenceValues) != len(selectedThirdSetValues) or len(secondToFirstDifferenceValues) != len(firstSetItemsPerYear):
			raise ValueError("Couldn't create a cohesive set of values for the time range of the first set")
			
		if sum(secondToFirstDifferenceValues) < 0:
			raise ValueError("Second set values are larger than the first set")
			
		if sum(thirdToSecondDifferenceValues) < 0:
			raise ValueError("Third set values are larger than the second set")
			
		if showRelativeValues:  # scale all values to be percentages of the total
			i = 0
			for value in selectedThirdSetValues:
				sumValues = value + thirdToSecondDifferenceValues[i] + secondToFirstDifferenceValues[i]
				if sumValues != 0:
					selectedThirdSetValues[i] = (value/sumValues)*100
					thirdToSecondDifferenceValues[i] = (thirdToSecondDifferenceValues[i]/sumValues)*100
					secondToFirstDifferenceValues[i] = (secondToFirstDifferenceValues[i]/sumValues)*100					
				i += 1
		
		data = [go.Bar(
				x=list(firstSetItemsPerYear.keys()),
				y=selectedThirdSetValues,
				text=self.formatOverlayHoverInfo(list(firstSetItemsPerYear.keys()), selectedThirdSetValues, nameThirdSet),
				hoverinfo='text',
				name=nameThirdSet,
				marker=dict(color=colours[0])
				),
				go.Bar(
				x=list(firstSetItemsPerYear.keys()),
				y=thirdToSecondDifferenceValues,
				text=self.formatOverlayHoverInfo(list(firstSetItemsPerYear.keys()), thirdToSecondDifferenceValues, nameDifferenceSecondAndThirdSet),
				hoverinfo='text',
				name=nameDifferenceSecondAndThirdSet,
				marker=dict(color=colours[1])
				),
				go.Bar(
				x=list(firstSetItemsPerYear.keys()),
				y=secondToFirstDifferenceValues,
				text=self.formatOverlayHoverInfo(list(firstSetItemsPerYear.keys()), secondToFirstDifferenceValues, nameDifferenceFirstAndSecondSet),
				hoverinfo='text',
				name=nameDifferenceFirstAndSecondSet,
				marker=dict(color=colours[2])
				)
				]

		layout = go.Layout(
			title=title,
			barmode='stack',
			xaxis=dict(
				title= xAxisTitle,
				titlefont=dict(family='Arial, monospace',size=18)
				),
			yaxis=dict(
				title= yAxisTitle,
				titlefont=dict(family='Arial, monospace',size=18)
			),
			separators = NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data=data, layout=layout)

		return fig

	def plotOverlayBarChartForThreeSetsItemsPerYear(self, firstSetItemsPerYear, secondSetItemsPerYear, thirdSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameDifferenceSecondAndThirdSet, nameThirdSet, title, xAxisTitle, yAxisTitle, filename, colours=[NISVHouseStyle.GREEN, NISVHouseStyle.ORANGE, NISVHouseStyle.GREY], showRelativeValues=False):
		"""
		Plots the third set of items per year, with stacked on this the difference of the second set with the third set
		of items, and stacked up on this the difference of the second set with the first set. The first set should have
		higher values than the second, and the second should have higher values than the third.
		The overall effect is to show the third set as one set of bars, with the difference between the sets on top,
		making it appear as if the third set is overlaid on the second, and the second set is overlaid on the first.
		When the user hovers over the bars with the mouse, the value of the third set will be shown next to the name
		'nameThirdSet',	the difference between the value of the first and second set will be shown next to the name
		'nameDifferenceFirstAndSecondSet, and the difference between the value of the second and third set will be shown
		next to the name 'nameDifferenceSecondAndThirdSet'.
		For example, if the first set contains all archive items, and the second set all items for which speech
		recognition is possible, and the third all items already with speech recognition, then appropriate labels would
		be 'speech recognition impossible' (for the first/second difference), 'waiting for speech recognition' (for the
		second/third difference) and 'speech recognition complete' (for the third set) 
		Expects that each itemsPerYear will be an ordered dictionary, with the year string as key, and the count as value.
		If the ranges of the years differ, the range of the first set is taken, and the 
		corresponding values looked up from the second and third set.  If they do not exist, an error is raised
		Filename should not contain a suffix, that will be added	
		if showRelativeValues is true, then the bars will be normalised to show them as percentages.
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
	"""
		
		fig = self.createOverlayBarChartFigureForThreeSetsItemsPerYear(firstSetItemsPerYear,secondSetItemsPerYear, thirdSetItemsPerYear, nameDifferenceFirstAndSecondSet, nameDifferenceSecondAndThirdSet, nameThirdSet, title, xAxisTitle, yAxisTitle, colours, showRelativeValues)

		self.__plotGraph(fig, filename)

	def createPieChartFigure(self, labels, values, title, margin, colors=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC], width = 950, height=600):
		"""creates a single pie chart figure with the given values and labels, optionally using the colours specified.
		If "colors" is empty, then default colours are used.
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns the Plotly figure as a dictionary"""
		
		if not labels:
			raise ValueError("Labels list is empty")
		
		if not values:
			raise ValueError("Values list is empty")
		
		if len(labels) != len(values):
			raise ValueError("Must have equal number of items in labels and values")
		
		trace = go.Pie(labels=labels, values=values, sort=False, textinfo='label+percent', textposition="outside",
					hoverinfo='value',
					hole=.4,
					showlegend=False,
					marker=dict(
								colors=colors,
								line=dict(color='#000000', width=2))
								)

		layout = go.Layout(title=title, width=width, height=height, margin=margin, separators=NISVHouseStyle.getSeparators())
		
		fig = go.Figure(data=[trace], layout=layout)
		
		return fig


	def plotPieChart(self, labels, values, title, margin, filename, colors=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC], width=950, height=600):
		"""Plots values and labels in a single pie chart, optionally using the colours specified.  If "colors" is empty,
		then default colours are used.  The chart is plotted under the given filename
		Optionally, you can enter a dict as the margin, to set the size of the graph margins (useful if text is
		overlapping). See plotly documentation for more information
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode"""

		fig = self.createPieChartFigure(labels, values, title, margin, colors, width, height)
		
		self.__plotGraph(fig, filename)

	def createFourPieChartsFigure(self, labelsLists, valuesLists, pieTitles, plotTitle, margin, colors=[NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC]):
		"""Creates a figure with up to 4 pie charts, arranged in a grid
		Returns the Plotly figure as a dictionary
		"""
		
		if len(valuesLists) > 4:
			raise ValueError("This function can only plot up to four pie charts")
			
		if len(labelsLists) != len(valuesLists):
			raise ValueError("Must have as many lists of labels as of values")
			
		if len(pieTitles) != len(valuesLists):
			raise ValueError("Must have as many pie titles as lists of values")

		lowerXBound = 0.45
		upperXBound = 0.55		
		lowerYBound = 0.45
		upperYBound = 0.55
		
		lowerXTextLocation = 0.15
		upperXTextLocation = 1.05
		lowerYTextLocation = -0.05
		upperYTextLocation = 0.55
		
		data = []
		annotations = []
		
		i = 0
		
		for valuesList in valuesLists:
			if i == 0:
				domain = dict(x=[0.0, lowerXBound], y=[upperYBound, 1])
				annotation = dict(font=dict(size = 40), showarrow=False, text=pieTitles[i], x=lowerXTextLocation, y=upperYTextLocation)
			elif i == 1:
				domain = dict(x=[0.0, lowerXBound], y=[0.0, lowerYBound])
				annotation = dict(font=dict(size = 40), showarrow=False, text=pieTitles[i], x=lowerXTextLocation, y=lowerYTextLocation)
			elif i == 2:
				domain = dict(x=[upperXBound, 1], y=[0.0, lowerYBound])				
				annotation = dict(font=dict(size = 40), showarrow=False, text=pieTitles[i], x=upperXTextLocation, y=lowerYTextLocation)
			elif i == 3:
				domain = dict(x=[upperXBound, 1], y=[upperYBound, 1])
				annotation = dict(font=dict(size=40), showarrow=False, text=pieTitles[i], x=upperXTextLocation, y=upperYTextLocation)

			# as we mainly use this set for the monitoring pie charts, choose to show the values on the chart, with the label and percent when hovering
			
			trace = go.Pie(labels=labelsLists[i], values=valuesList,
				hoverinfo='label+percent', textinfo='value',
				textfont=dict(size=20),
				hole=.4,
				name=pieTitles[i],
				domain=domain,
				marker=dict(
							colors=colors,
							line=dict(color='#000000', width=2)
							)
				)

			data.append(trace)
			annotations.append(annotation)
			
			i += 1
			
		layout = go.Layout(
		legend=dict(x=0.8, y=0.6),
		title=plotTitle,
		autosize=False, 
		width=750,
		height=1100,
		margin=margin,
		annotations=annotations,
		separators=NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data = data, layout = layout)
		return fig
		
		
	def plotFourPieCharts(self, labelsLists, valuesLists, pieTitles, plotTitle, margin, filename, colors= [NISVHouseStyle.BLUE, NISVHouseStyle.PINK,NISVHouseStyle.GREEN,NISVHouseStyle.ORANGE, NISVHouseStyle.GREY,NISVHouseStyle.YELLOW,NISVHouseStyle.PURPLE,NISVHouseStyle.LILAC]):
		"""Plots up to 4 pie charts, arranged in a grid.  Plot is given the filename
		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createFourPieChartsFigure(labelsLists, valuesLists, pieTitles, plotTitle, margin, colors)
		self.__plotGraph(fig, filename)
		
	def createClipLocationsInTimeLinesFigure(self, timelineList, colors, title, date):
		"""Creates a figure showing the clip locations in their respective timelines, with the timelines under each
		other, and the given title.
		You can fill in the colors array to choose the colours for the timeline and clips, if the array is empty then
		defaults are used, which are suitable for up to 6 clips per timeline.  Colours should be specified using
		rgb(r,g,b) e.g. rgb(66,124,233) or hex e.g. "#e00034"
		timelineList should be a dictionary, with timeline names/IDs as keys. 
		The visualisation is plotted under the given filename
		It is assumed that all clip start and end times fall within the given timeline duration, and do not overlap
		date is needed to make the timeline visualisation work, this can be any date in the format yyyy-mm-dd
		Each timeline should contain the following keys:
		"name" - timeline name or identifier
		"startTime" - start of timeline in format HH:MM:SS
		"endTime" - end of timeline in format HH:MM:SS
		"clips" a list of clips, (this can be empty, then only the timeline is shown)
		each clip containing the following keys:
		"startTime" - start time of the clip in format HH:MM:SS
		"endTime" - end time of the clip in format HH:MM:SS

		Returns the Plotly figure as a dictionary
		"""
		
		if not timelineList:
			raise ValueError("Timeline list is empty")
			
		if not date:
			raise ValueError("Date is empty")
		
		df = []
		clipColors =  {}
		
		# initialise a colors dictionary with colours per timeline and per clip within a timeline
		if colors:
			clipColors["timeline"] = colors[0]
			i = 1
			for color in colors[1:]:
				clipColors["clip" + str(i-1)] = colors[i]
				i=i+1
		else:  # use default values, specifies good colours for up to 6 clips per timeline
			
			clipColors = {'timeline': NISVHouseStyle.GREY,
				'clip0': NISVHouseStyle.PINK,
				'clip1': NISVHouseStyle.BLUE,
				'clip2': NISVHouseStyle.GREEN,
				'clip3': NISVHouseStyle.LILAC,
				'clip4': NISVHouseStyle.ORANGE,
				'clip5': NISVHouseStyle.YELLOW}

		for timeline in timelineList:

			if "name" not in timeline or "startTime" not in timeline or "endTime" not in timeline or "clips" not in timeline:
				raise ValueError("Timeline must contain the keys \"name\", \"startTime\", \"endTime\" and \"clips\"")

			df.append(dict(Task=timeline["name"], Start=date + " " + timeline["startTime"], Finish=date + " " + timeline["endTime"], Resource="timeline"))
				
			i = 0
			
			if not isinstance(timeline["clips"], list):
				raise ValueError("Clips must be a list of dictionaries")
				
			if (len(timeline["clips"]) + 1) > len(clipColors):
				raise ValueError("You have specified too few colours, you need as many colours as the maximum number of clips per timeline plus one for the timeline itself")
			
			for clip in timeline["clips"]:
				if "startTime" not in clip or "endTime" not in clip:
					raise ValueError("Clip must contain the keys \"startTime\" and \"endTime\"")
				
				df.append(dict(Task=timeline["name"], Start= date + " " + clip["startTime"], Finish= date + " " + clip["endTime"],Resource="clip"+str(i)))
				i += 1

		fig = ff.create_gantt(df, colors=clipColors, index_col='Resource', title=title, group_tasks=True)
		
		return fig

	def visualiseClipLocationsInTimeLines(self, timelineList, colors, title, date, filename):
		"""Plots the clip locations in their respective timelines, with the timelines under each other, and the given
		title.
		You can fill in the colors array to choose the colours for the timeline and clips, if the array is empty then
		defaults are used, which are suitable for up to 6 clips per timeline.  Colours should be specified using
		rgb(r,g,b) e.g. rgb(66,124,233) or hex e.g. "#e00034"
		timelineList should be a dictionary, with timeline names/IDs as keys. 
		The visualisation is plotted under the given filename
		It is assumed that all clip start and end times fall within the given timeline duration, and do not overlap
		date is needed to make the timeline visualisation work, this can be any date in the format yyyy-mm-dd
		Each timeline should be a dictionary containing the following keys:
		"name" - timeline name or identifier
		"startTime" - start of timeline in format HH:MM:SS
		"endTime" - end of timeline in format HH:MM:SS
		"clips" a list of clips, (this can be empty, then only the timeline is shown) each clip containing the following keys:
		"startTime" - start time of the clip in format HH:MM:SS
		"endTime" - end time of the clip in format HH:MM:SS
		"description"- a very short description that should appear when hovering

		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createClipLocationsInTimeLinesFigure(timelineList, colors, title, date)
		
		self.__plotGraph(fig, filename)
		
	def createSimpleTimelinesFigure(self, timelineList, height, width, title, margin=None):
		"""Creates a figure with bars for the respective timelines, with the timelines under each other, and the given
		title.
		timelineList should be a dictionary, with timeline names as keys. 

		Each timeline should be a dictionary containing the following keys:
		"name" - timeline name or identifier
		"startDate" - start of timeline in format yyyy-mm-dd
		"endDate" - end of timeline in format yyyy-mm-dd
		"description"- a very short description that should appear when hovering
		
		The height and width of the figure are also set. The margin is an optional parameter, this can be 
		very useful for adjusting the size of the y axis labels to allow the names of the timelines to fit.
		E.g. margin = dict(l=110)

		Returns the Plotly figure as a dictionary
		"""
		
		if not timelineList:
			raise ValueError("Timeline list is empty")
		
		df = []
		timelineColors = []
		i = 0
		for timeline in timelineList:
			
			if "name" not in timeline or "startDate" not in timeline or "endDate" not in timeline or "description" not in timeline:
				raise ValueError("Timeline must contain the keys \"name\", \"startDate\", \"endDate\" and \"description\"")
				
			df.append(dict(Task=timeline["name"], Start=timeline["startDate"], Finish= timeline["endDate"], Resource= "timeline" + str(i), Description = timeline["description"]))
			timelineColors.append(NISVHouseStyle.BLUE)
			i += 1
		
		fig = ff.create_gantt(df, colors=timelineColors, index_col='Resource', title=title, height=height, width=width)

		# set hover info to only show the description
		for trace in fig['data']:
			trace.update(hoverinfo="text")
			
		if margin:
			fig['layout'].update(autosize=False, width=width, height=height, margin=margin)
			
		return fig
		
	def visualiseSimpleTimeLines(self, timelineList, height, width, title, filename, margin=None):
		"""Plots bars for the respective timelines, with the timelines under each other, and the given title.  
timelineList should be a dictionary, with timeline names as keys. 
		The visualisation is plotted under the given filename

		Each timeline should be a dictionary containing the following keys:
		"name" - timeline name or identifier
		"startDate" - start of timeline in format yyyy-mm-dd
		"endDate" - end of timeline in format yyyy-mm-dd

		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createSimpleTimelinesFigure(timelineList, height, width, title, margin)
		
		self.__plotGraph(fig, filename)

	def createUpdateTimeFigure(self, lastUpdated):
		"""Creates a figure showing the last updated time.  No axes are shown.  In offline mode, the link and mode bar 
		are automatically excluded. To also exclude the link and mode bar from online plots, see
		https://help.plot.ly/embed-graphs-in-websites/#step-8-customize-the-iframe

		Returns the Plotly figure as a dictionary
		"""

		label_trace = go.Scatter(
			x=[1],
			y=[1],
			mode='text',
			text=["Last updated: %s"%lastUpdated],
			textfont=dict(
				color="rgb(0,0,0)",
				size=15
			)
		)

		data = [label_trace]

		layout = go.Layout(
			height=50,
			width=500,
			showlegend=False,
			xaxis=dict(
				showticklabels=False,
				showgrid=False,
				zeroline=False,
			),
			yaxis=dict(
				showticklabels=False,
				showgrid=False,
				zeroline=False
			),
			margin=dict(t=0, b=0),
			separators=NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data=data, layout=layout)
		
		return fig	
		
	def showUpdateTime(self, lastUpdated, filename):
		"""Writes the last updated time to a plotly chart.  No axes are shown.  In offline mode, the link and mode bar 
		are automatically excluded. To also exclude the link and mode bar from online plots, see
		https://help.plot.ly/embed-graphs-in-websites/#step-8-customize-the-iframe

		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createUpdateTimeFigure(lastUpdated)		
		
		config = {"showLink": False, "displayModeBar": False}
		
		self.__plotGraph(fig, filename, config)
		
	def createFunnelChart(self, labels, values, colours, plotTitle):
		"""Creates a funnel chart with the values for each section.  Adapted from the example on
		https://plot.ly/python/funnel-charts/

		Returns the Plotly figure as a dictionary
		"""
		
		text_colour = 'rgb(0,0,0)'
		background_colour = 'rgb(255,255,255)'
		n_phase = len(labels)
		plot_width = 400

		# height of a section and difference between sections 
		section_h = 100
		section_d = 10

		# multiplication factor to calculate the width of other sections
		unit_width = plot_width / max(values)

		# width of each funnel section relative to the plot width
		phase_w = [int(value * unit_width) for value in values]

		# plot height based on the number of sections and the gap in between them
		height = section_h * n_phase + section_d * (n_phase - 1)
		
		# list containing all the plot shapes
		shapes = []

		# list containing the Y-axis location for each section's name and value text
		label_y = []

		for i in range(n_phase):
				if i == n_phase-1:
						points = [phase_w[i] / 2, height, phase_w[i] / 2, height - section_h]
				else:
						points = [phase_w[i] / 2, height, phase_w[i+1] / 2, height - section_h]

				path = 'M {0} {1} L {2} {3} L -{2} {3} L -{0} {1} Z'.format(*points)

				shape = {
						'type': 'path',
						'path': path,
						'fillcolor': colours[i],
						'line': {
							'width': 1,
							'color': colours[i]
						}
				}
				shapes.append(shape)

				# Y-axis location for this section's details (text)
				label_y.append(height - (section_h / 2))

				height = height - (section_h + section_d)
				
		# For phase names
		
		# To allow slightly longer phase names to be displayed fully, the scatter
		# graph needs to be wider.  A hack to fix this is to add a data point at
		# the beginning that is placed further to the left
		xPhase = []
		xPhase.append(-400)
		xPhase.extend([-350]*n_phase)
		yPhase = []
		yPhase.append(0)
		yPhase.extend(label_y)
		textLabels = []
		textLabels.append(""),
		textLabels.extend(labels)
		
		label_trace = go.Scatter(
			x=xPhase,
			y=yPhase,
			mode='text',
			text=textLabels,
			textfont=dict(
				color=text_colour,
				size=15
			)
		)

		# For phase values
		value_trace = go.Scatter(
			x=[350]*n_phase,
			y=label_y,
			mode='text',
			text=values,
			textfont=dict(
				color= text_colour,
				size=15
			)
		)

		data = [label_trace, value_trace]

		layout = go.Layout(
			title= plotTitle,
			titlefont=dict(
				size=20,
				color=text_colour
			),
			shapes=shapes,
			height=560,
			width=800,
			showlegend=False,
			paper_bgcolor=background_colour,
			plot_bgcolor=background_colour,
			xaxis=dict(
				showticklabels=False,
				zeroline=False,
				showgrid=False
			),
			yaxis=dict(
				showticklabels=False,
				zeroline=False,
				showgrid=False
			), 
			separators=NISVHouseStyle.getSeparators()
		)

		fig = go.Figure(data=data, layout=layout)
		return fig
		
	def plotFunnelChart(self, labels, values, colours, plotTitle, filename):
		"""Plots a funnel chart with the values for each section.  Adapted from the example on
		https://plot.ly/python/funnel-charts/

		Returns no values, the graph is written to the Plotly website, to a HTML file, or displayed depending on the mode
		"""

		fig = self.createFunnelChart(labels, values, colours, plotTitle)
		self.__plotGraph(fig, filename)
