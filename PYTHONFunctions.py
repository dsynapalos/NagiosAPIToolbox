from datetime import datetime, timedelta
import re, os


def getDates(datafiles):
    dateList = []
    for datafile in datafiles:
        dateList.append(
            datetime.strptime(re.search('(\d+-\d+-\d+)\..+', os.path.basename(datafile)).group(1), '%d-%m-%y'))
    startDate = sorted(dateList)[0].strftime('%d/%m/%Y')
    endDate = sorted(dateList)[-1].strftime('%d/%m/%Y')
    toDate = datetime.today().strftime('%d/%m/%Y')
    toMorrow = (datetime.today() + timedelta(days=1)).strftime('%d/%m/%Y')
    return startDate, endDate, toDate, toMorrow
