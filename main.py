import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
from ShareTimes import ShareTimes

# Constants
PLOT_DPI = 300  # The DPI at which the plots are generated
AVERAGE_DECIMAL_COUNT = 5  # The amount of decimals to display in the plot for the average values
AVERAGE_TIME_SECONDS_DECIMAL_COUNT = 2  # The amount of decimals to display whenever showing times


def readLog(filePaths: [str]):
	"""
	Reads the given log file and extracts the difficulty of each found share

	:param filePaths: The file names of the log files. Have to be in the same directory or the path (abs / rel) has to be given. Has to be an array of strings.
	"""
	difs = []  # Will be filled with share difficulties in GH
	lines = []  # Will be filled with the read lines of log

	# Read all log files into the lines list
	linesPerFile = readLines(filePaths)
	# Flattens the nested list of lines into one list
	lines = [line for file in linesPerFile for line in file]

	# Get the difficulties from the lines
	difs = getDifficulties(lines)

	# Calculate average values and draw plots
	drawPlots(difs)

	# Print the list of difs
	difs.sort(reverse=True)
	if len(difs) > 10:
		print("10 best difficulties: {}".format(difs[:10]))
	else:
		print("Difficulties: {}".format(difs))

	# Print the number of difs
	print("# Shares: {}".format(len(difs)))
	print("# Dev Shares: {}".format(getAmountOfDefShares(lines)))

	# Print the total difficulty of found shares
	print("Total difficulty: {} GH".format(sum(difs).__round__(AVERAGE_DECIMAL_COUNT)))

	# Get required mining information
	shareTimes = getAvgTimeForShare(linesPerFile)

	# Print the total time spent mining
	totalMiningSeconds = shareTimes.totalTimeSpentMining
	totalMiningMinutes = (totalMiningSeconds / 60).__round__(AVERAGE_TIME_SECONDS_DECIMAL_COUNT)
	totalMiningHours = (totalMiningMinutes / 60).__round__(AVERAGE_TIME_SECONDS_DECIMAL_COUNT)
	totalMiningDays = (totalMiningHours / 24).__round__(AVERAGE_TIME_SECONDS_DECIMAL_COUNT)
	print("Total time spent mining: {}s ({}min, {}h, {}d)".format(totalMiningSeconds, totalMiningMinutes,
																  totalMiningHours, totalMiningDays))

	# Get average time per share
	print("Average time per share in seconds: {}".format(
		shareTimes.avgTimePerShare.__round__(AVERAGE_TIME_SECONDS_DECIMAL_COUNT)))


def getDifficulties(lines: [str]) -> [float]:
	"""
	Reads the given log lines and extracts the difficulties of the found shares.

	:param lines: The lines of the log files
	:return: The list of difficulties as float. Difficulties are calculated into GH.
	"""
	difs: [float] = []

	for line in lines:
		# Regex matches e.g.: Eth: Share actual difficulty: 28.2 GH
		regex = re.compile('Eth: Share actual difficulty: [0-9]+([.][0-9])? [A-Z]H')

		matches = re.search(regex, line)

		# If line contains details of found share, extract the difficulty value
		if matches:
			currentMatch = matches.group(0)

			# Regex matches e.g.: 28.2
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
	lines = [[]]

	for filePath in filePaths:
		with open(filePath, "r") as file:
			lines.append(file.readlines())

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
		# Regex matches e.g.: DevFee: Share actual difficulty: 28.2 GH
		regex = re.compile('DevFee: Share actual difficulty: [0-9]+([.][0-9])? [A-Z]H')

		matches = re.search(regex, line)

		if matches:
			numberOfDevShares += 1

	return numberOfDevShares


def getAvgTimeForShare(files: [[str]]) -> ShareTimes:
	"""
	Calculates the average time spent to find a share. Also returns the total time spent mining

	:param lines: The lines for each given log file
	:return: A ShareTimes object containing the average time per share and the total mining time
	"""
	numberOfShares = 0  # The number of found shares
	totalTimeMining = 0  # The total time spent mining to calculate avg per share later

	for file in files:
		# This resets the lastFoundShareTime every time a new log file is read.
		# This is to ensure that no wrong results are calculated if there has been an interruption between
		# two mining sessions
		lastFoundShareTime = None

		for line in file:
			# Regex matches e.g.: Eth: Share actual difficulty: 28.2 GH
			regex = re.compile('Eth: Share actual difficulty: [0-9]+([.][0-9])? [A-Z]H')

			matches = re.search(regex, line)

			# If line contains details of found share, extract the time when the share was found
			if matches:
				# Regex matches e.g.: 2021.01.12:09:00:37
				datetimeRegex = re.compile('[0-9]{4}\.[0-9]{2}\.[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}')

				datetimeString = re.search(datetimeRegex, line).group(0)

				# Parse to datetime format so we can work with it
				foundDatetime = datetime.strptime(datetimeString, "%Y.%m.%d:%H:%M:%S")

				# Calculate time since the last share was found. If this is the first found share, it is not taken
				# into consideration which does make the result slightly incorrect but makes it easier to calculate.
				# TODO: Might be fixed later if I'm in the mood.
				if lastFoundShareTime:
					# Increase total number of found shares so calculation is right
					numberOfShares += 1

					# Calculate time since last share was found
					timeSinceLastShare = (foundDatetime - lastFoundShareTime).total_seconds()
					totalTimeMining += timeSinceLastShare
					lastFoundShareTime = foundDatetime
				else:
					# Don't update the number of found shares so the deviation we get through this problem with
					# not accounting for the first share is minimal
					lastFoundShareTime = foundDatetime

	avgTimePerShare = (totalTimeMining / numberOfShares)

	retShareTime = ShareTimes(avgTimePerShare, totalTimeMining)

	return retShareTime


if __name__ == "__main__":
	readLog([])
