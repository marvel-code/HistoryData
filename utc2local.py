from shutil import copyfile
from pathlib import Path
from datetime import datetime
import os


# Constants


ADD_HOURS = 3
NEW_TIME_ZONE = '+03:00'
DAYTRADES_FILENAME = 'trades.csv'
TRADESDATES_FILENAME = 'tradesCsvDates.txt'
NEW_HISTORYDATA_PATH = './DTR_HistoryData'
CONVERTEDDATES_PATH = './converteddates.txt'

print(f'ADD_HOURS {ADD_HOURS}')
print(f'NEW_TIME_ZONE {NEW_TIME_ZONE}')


# Methods


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
        dstHour = srcHour + ADD_HOURS
        dataArray[0] = str(dstHour) + dataArray[0][2:]
        # Change timezone
        dataArray[1] = NEW_TIME_ZONE
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


# Main


nowDateStr = datetime.now().strftime('%Y_%m_%d')
srcRDir = f'R/'

fdConvertedDates = open(CONVERTEDDATES_PATH, 'a+')
convertedDates = getConvertedDates(fdConvertedDates)
print('Converted dates:', convertedDates)

# Securities
securities2convert = getDirsFromPath(srcRDir)
print('Securities to convert:', securities2convert)
for security in securities2convert:
    print('Security:', security)
    try:
        srcSecurityDir = f'{srcRDir}/{security}/'
        dstRDir = f'{NEW_HISTORYDATA_PATH}/R/'
        dstSecurityDir = f'{dstRDir}/{security}/'

        # Date dirs convertion
        dateDirs = getDirsFromPath(srcSecurityDir)
        print('Date dirs:', dateDirs)
        for dateDir in dateDirs:
            if dateDir not in convertedDates:
                srcdateDir = f'{srcSecurityDir}/{dateDir}'
                srcFilePath = f'{srcdateDir}/{DAYTRADES_FILENAME}'
                fdSrc = open(srcFilePath, 'r')

                # Convertion pipe
                try:
                    dstdateDir = f'{dstSecurityDir}/{dateDir}'
                    dstFilePath = f'{dstdateDir}/{DAYTRADES_FILENAME}'

                    mkdir(dstdateDir)
                    fdDst = open(dstFilePath, 'w+')
                    convert(fdSrc, fdDst)

                    if nowDateStr != dateDir:
                        addDate(fdConvertedDates, dateDir)
                except Exception:
                    print('-  Convertion exception')

        # Trades dates copy
        copyfile(f'{srcSecurityDir}/{TRADESDATES_FILENAME}', f'{dstSecurityDir}/{TRADESDATES_FILENAME}')
    except Exception:
        print('- Security exception')
