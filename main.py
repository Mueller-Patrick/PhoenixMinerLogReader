import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Constants
PLOT_DPI = 300
AVERAGE_DECIMAL_COUNT = 5


def readLog(filePaths: [str]):
	"""
	Reads the given log file and extracts the difficulty of each found share
	:param filePaths: The file names of the log files. Have to be in the same directory or the path (abs / rel) has to be given. Has to be an array of strings.
	:return: Void
	"""
	difs = []  # Will be filled with share difficulties in GH
	lines = []  # Will be filled with the read lines of log

	# Read all log files into the lines list
	for filePath in filePaths:
		with open(filePath, "r") as file:
			lines.extend(file.readlines())

	# Go through every read line
	for line in lines:
		regex = re.compile('Share actual difficulty: [0-9]+([.][0-9])? [MGT]H')

		matches = re.search(regex, line)

		# If line contains details of found share, extract the difficulty value
		if matches:
			currentMatch = matches.group(0)

			difRegex = re.compile('[0-9]+([.][0-9])?')

			difMatch = str(re.search(difRegex, currentMatch).group(0))

			difInt = float(difMatch)

			# Calculate difficulty to GH to have a comparable value across all shares
			if 'MH' in currentMatch:
				difs.append(difInt / 1000)
			elif 'GH' in currentMatch:
				difs.append(difInt)
			else:
				difs.append(difInt * 1000)

	# Calculate average value
	sum = 0
	for entry in difs:
		sum += entry
	avgVal = (sum / len(difs)).__round__(AVERAGE_DECIMAL_COUNT)

	# Calculate top 10% avg
	sum = 0
	sortedDifs = difs.copy()
	sortedDifs.sort(reverse=True)
	for entry in sortedDifs[:round(len(difs) / 10)]:
		sum += entry
	top10Avg = (sum / round(len(difs) / 10)).__round__(AVERAGE_DECIMAL_COUNT)

	# Set plot dpi to desired value
	mpl.rcParams['figure.dpi'] = PLOT_DPI

	# Draw the plot
	drawPlot(difs, avgVal, top10Avg)
	drawHistogram(difs)

	# Print the list of difs
	difs.sort(reverse=True)
	print(difs)


def drawPlot(difs, avgVal, top10Avg):
	plt.plot(difs)
	plt.axhline(avgVal, color='r')
	plt.axhline(top10Avg, color='g')
	plt.legend(['Difficulty', ('Avg = {} GH'.format(avgVal)), ('Top 10% Avg: {} GH'.format(top10Avg))])
	plt.show(block=True)


def drawHistogram(difs):
	plt.hist(difs, bins=len(difs))
	plt.show(blcok=True)


if __name__ == "__main__":
	readLog([])
