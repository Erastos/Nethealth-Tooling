import csv
from enum import Enum

files = {
    "Comm": "./NetHealth Data/CommEvents(2-28-20)_study_start.csv",
    "Basic": "./NetHealth Data/BasicSurvey(3-6-20).csv",
    "Network": "./NetHealth Data/NetWorkSurvey(2-28-20).csv"
}


class Headers(Enum):
    EPOCHTIME = 0
    DATE = 1
    TIME = 2
    DAYOFWEEK = 3
    INSESSION = 4
    STUDYWEEK = 5
    STUDYDAY = 6
    EGOID = 7
    EGOCONF = 8
    ALTERID = 9
    ALTERCONF = 10
    OUTGOING = 11
    IPHONE = 12
    EVENTTYPE = 13
    EVENTTYPEDETAIL = 14
    MESSAGETYPE = 15
    DURATION = 16
    LENGTH = 17
    BYTES = 18


def load_data(filename, numRecords):
    """Loads Data From File using a generator"""
    file = open(filename, 'r', buffering=1)
    reader = csv.reader(file)
    next(reader)
    result = []

    for i, row in enumerate(reader):
        if numRecords != 0 and i > numRecords:
            break
        result.append(row)
    return result


def open_files(numRecords):
    comm = load_data(files['Comm'], numRecords)
    basic = load_data(files['Basic'], 0)
    network = load_data(files['Network'], 0)
    return comm, basic, network


if __name__ == '__main__':
    num_of_records = 100000
    ld = load_data(files["Comm"], num_of_records)
    results = []
    for i in ld:
        results.append(i)
