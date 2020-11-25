from shutil import copyfile
from pathlib import Path
import os

# Constants

ADD_HOURS = 3
NEW_TIME_ZONE = '+03:00'
DAYTRADES_FILENAME = 'trades.csv'
TRADESDATES_FILENAME = 'tradesCsvDates.txt'
NEW_HISTORYDATA_PATH = './DTR_HistoryData'
CONVERTEDDATES_PATH = './converteddates.txt'

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

# Main

srcRDir = f'R/'
# Securities
securities2convert = getDirsFromPath(srcRDir)
print('Securities to convert:', securities2convert)
for security in securities2convert:
    print('Security:', security)
    try:
        srcSecurityDir = f'{srcRDir}/{security}/'
        # Date dirs
        dateDirs = getDirsFromPath(srcSecurityDir)
        print('Date dirs:', dateDirs)
        for dateDir in dateDirs:
            srcdateDir = f'{srcSecurityDir}/{dateDir}'
            srcFilePath = f'{srcdateDir}/{DAYTRADES_FILENAME}'
            fdSrc = open(srcFilePath, 'r')
            # Convertion pipe
            try:
                dstRDir = f'{NEW_HISTORYDATA_PATH}/R/'
                dstSecurityDir = f'{dstRDir}/{security}/'
                dstdateDir = f'{dstSecurityDir}/{dateDir}'
                dstFilePath = f'{dstdateDir}/{DAYTRADES_FILENAME}'

                mkdir(dstdateDir)
                fdDst = open(dstFilePath, 'w+')
                convert(fdSrc, fdDst)
            except Exception:
                print('-  Convertion exception')
        # Trades dates copy
        copyfile(f'{srcSecurityDir}/{TRADESDATES_FILENAME}', f'{dstSecurityDir}/{TRADESDATES_FILENAME}')
    except Exception:
        print('- Security exception')
