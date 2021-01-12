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
	"""
	difs = []  # Will be filled with share difficulties in GH
	lines = []  # Will be filled with the read lines of log

	# Read all log files into the lines list
	lines = readLines(filePaths)

	# Get the difficulties from the lines
	difs = getDifficulties(lines)

	# Calculate average values and draw plots
	drawPlots(difs)

	# Print the list of difs
	difs.sort(reverse=True)
	print(difs)
	print("Dev Shares: {}".format(getAmountOfDefShares(lines)))


def getDifficulties(lines: [str]) -> [float]:
	"""
	Reads the given log lines and extracts the difficulties of the found shares.

	:param lines: The lines of the log files
	:return: The list of difficulties as float. Difficulties are calculated into GH.
	"""
	difs: [float] = []

	for line in lines:
		regex = re.compile('Eth: Share actual difficulty: [0-9]+([.][0-9])? [A-Z]H')

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
			elif 'TH' in currentMatch:
				difs.append(difInt * 1000)
			else:
				print("Found something other than MH / GH / TH. Please verify that this is correct and report it as"
					  + " an issue at https://github.com/Mueller-Patrick/PhoenixMinerLogReader/issues")

	return difs

def drawPlots(difs: [float]):
	"""
	Calculates required values and then draws the plot for the difficulties of the found shares

	:param difs: The list of difficulties
	"""
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


def readLines(filePaths: [str]) -> [str]:
	"""
	Reads the given files and returns a list of lines of all files.
	Reads the files in the order that they were given.

	:param filePaths: A list of file paths or file names.
	:return: A list of strings, each entry representing one line of a file
	"""
	lines = []

	for filePath in filePaths:
		with open(filePath, "r") as file:
			lines.extend(file.readlines())

	return lines


def drawPlot(difs: [float], avgVal: float, top10Avg: float):
	"""
	Draw the line graph that shows the difficulty of found shares over time

	:param difs: The array of difficulties
	:param avgVal: The average of all difficulties
	:param top10Avg: The average of the top 10 difficulties
	"""
	plt.plot(difs)
	plt.axhline(avgVal, color='r')
	plt.axhline(top10Avg, color='g')
	plt.legend(['Difficulty', ('Avg = {} GH'.format(avgVal)), ('Top 10% Avg: {} GH'.format(top10Avg))])
	plt.show(block=True)


def drawHistogram(difs):
	plt.hist(difs, bins=len(difs))
	plt.show(blcok=True)


def getAmountOfDefShares(lines: [str]) -> int:
	"""
	Returns the number of shares that went into the algorithm developers account

	:param lines: The lines of the log files
	:return: The amount of dev shares
	"""
	numberOfDevShares = 0
	for line in lines:
		regex = re.compile('DevFee: Share actual difficulty: [0-9]+([.][0-9])? [A-Z]H')

		matches = re.search(regex, line)

		if matches:
			numberOfDevShares += 1

	return numberOfDevShares


if __name__ == "__main__":
	readLog([])
