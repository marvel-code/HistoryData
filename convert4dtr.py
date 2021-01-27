from shutil import copyfile
from pathlib import Path
from datetime import datetime
import os
import json


## Constants


with open('convert4dtr_settings.json') as fdSettings:
	SETTINGS = json.load(fdSettings)
	print(SETTINGS)


## Methods


def getDirsFromPath(path):
    dirs = []
    for dir in Path(path).iterdir():
        if dir.is_dir():
            dirs.append(dir.name)
    return dirs

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def convert(fdSrc, fdDst):
    for line in fdSrc:
        dataArray = line.split(';')
        # Change hour
        srcHour = int(dataArray[0][:2])
        dstHour = srcHour + SETTINGS["hours2add"]
        dataArray[0] = f'{dstHour:02}{dataArray[0][2:]}'
        # Change timezone
        dataArray[1] = SETTINGS['newtimezone']
        # Print
        dstLine = ';'.join(dataArray)
        fdDst.write(dstLine)

def getConvertedDates(fdConvertedDates):
    fdConvertedDates.seek(0)
    convertedDates = set()
    for date in fdConvertedDates:
        convertedDates.add(date.strip())

    return convertedDates

def addDate(fdConvertedDates, dateDirName):
    fdConvertedDates.write(f'{dateDirName}\n')


## Main


nowDateStr = datetime.now().strftime('%Y_%m_%d')
srcRDir = f'R/'

with open(SETTINGS['converteddates_path'], 'a+') as fdConvertedDates:
	convertedDates = getConvertedDates(fdConvertedDates)
	print('Converted dates:', convertedDates)

	# Securities
	securities2convert = getDirsFromPath(srcRDir)
	print('Securities to convert:', securities2convert)
	for security in securities2convert:
		print('Security:', security)
		try:
			srcSecurityDir = f'{srcRDir}/{security}/'
			dstRDir = f'{SETTINGS["newhistorydata_path"]}/R/'
			dstSecurityDir = f'{dstRDir}/{security}/'

			# Date dirs convertion
			dateDirs = getDirsFromPath(srcSecurityDir)
			print('Date dirs:', dateDirs)
			for dateDir in dateDirs:
				if dateDir not in convertedDates:
					srcdateDir = f'{srcSecurityDir}/{dateDir}'
					srcFilePath = f'{srcdateDir}/{SETTINGS["daytrades_filename"]}'
					with open(srcFilePath, 'r') as fdSrc:

						# Convertion pipe
						try:
							dstdateDir = f'{dstSecurityDir}/{dateDir}'
							dstFilePath = f'{dstdateDir}/{SETTINGS["daytrades_filename"]}'

							mkdir(dstdateDir)
							with open(dstFilePath, 'w+') as fdDst:
								convert(fdSrc, fdDst)

								if nowDateStr != dateDir:
									addDate(fdConvertedDates, dateDir)
						except Exception as e:
							print(e)
							print('-  Convertion exception')

			# Trades dates copy
			copyfile(f'{srcSecurityDir}/{SETTINGS["tradedates_filename"]}', f'{dstSecurityDir}/{SETTINGS["tradedates_filename"]}')
		except Exception:
			print('- Security exception')
			