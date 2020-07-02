import pandas as pd
import csv

# Location of files to pull data from
files = {
    "Network Survey": "NetHealth Data/NetWorkSurvey(2-28-20).csv",
    "Basic Survey": "NetHealth Data/BasicSurvey(3-6-20).csv",
    "CommEvents": "NetHealth Data/CommEvents(2-28-20)_study_start.csv"
}


def find_line_num_date(file_name, date):
    """Function to the line number of a specific date"""
    reader = csv.reader(open(file_name, "r"))
    headers = next(reader)
    for i, line in enumerate(reader):
        if line[headers.index("date")] == date:
            return i


def open_files(number_of_records):
    """Open Nethealth Data Files"""
    network = pd.read_csv(files["Network Survey"], low_memory=False)
    basic = pd.read_csv(files["Basic Survey"], low_memory=False)
    comm = pd.read_csv(files["CommEvents"], nrows=number_of_records, low_memory=False)
    return network, basic, comm


def retrieve_ego_data(egoID):
    """Retrieve date regarding a specific egoID"""
    egoID_data = comm["egoid"] == egoID
    return comm[egoID_data]


def remove_outlier_data():
    """Removes outlier communication data as specified by the Nethealth Study"""
    # Remove Calls of 0 Duration
    calls = comm["eventtype"] == "Call"
    zero_duration = comm["duration"] == 0.0
    calls_zero = comm[calls & zero_duration].index
    comm.drop(calls_zero, inplace=True)

    # Remove messages of 0 length
    zero_length = comm[comm["length"] == 0].index
    zero_bytes = comm[comm["bytes"] == 0].index

    comm.drop(zero_length, inplace=True)
    comm.drop(zero_bytes, inplace=True)

    # WhatsApp Group Messages
    whats_app_gc = comm[comm["eventtypedetail"] == "GC"].index
    comm.drop(whats_app_gc, inplace=True)


def collect_clubs():
    """Gets club information about all egoids in the dataset"""
    clubs = {}
    for club_num in range(1, 11):
        club_variable = "club{}rc_2".format(club_num)
        club_i = basic[["egoid", club_variable]]
        for egoid, club in zip(club_i['egoid'], club_i[club_variable]):
            if not pd.isna(club) and str(club)[0] != '9':
                if club in clubs:
                    clubs[club].add(egoid)
                else:
                    club_set = set()
                    club_set.add(egoid)
                    clubs[club] = club_set
    return clubs


def ego_get_club(egoid):
    """Get clubs belonging to specific egoid"""
    clubs = []
    is_egoid = basic["egoid"] == egoid
    for club_num in range(1, 11):
        club_variable = "club{}rc_2".format(club_num)
        clubs.append(basic[is_egoid][club_variable])


def compare_clubs_comm(clubs):
    """Maps the club data onto the communication data"""
    for club in clubs:
        hit_counter = 0
        total_message_count = 0
        for egoid in clubs[club]:
            counted = []
            egoid_data = retrieve_ego_data(egoid)
            for alterid in egoid_data["alterid"]:
                if alterid in clubs[club]:
                    hit_counter += 1
                    counted.append(alterid)
                total_message_count += 1
        if total_message_count > 0:
            print("Club: {} : {} - {:.2%}".format(club, hit_counter, hit_counter / total_message_count))


def compare_clubs_network(clubs, wave_num):
    """Compare Club Data to Network Data"""
    wave_variable = "Wave" + str(wave_num)
    for club in clubs:
        hit_counter = 0
        for egoid in clubs[club]:
            egoid_network = network["egoid"] == egoid
            wave_condtion = network["wave"] == wave_variable
            egoid_network_data = network[egoid_network & wave_condtion]
            for alterid in egoid_network_data["alterid"]:
                if alterid in clubs[club]:
                    hit_counter += 1
                    break
        print("Club: {} : {} - {:.2%}".format(club, hit_counter, hit_counter / len(clubs[club])))


if __name__ == '__main__':
    network, basic, comm = open_files(200000)
    remove_outlier_data()
    compare_clubs_network(collect_clubs(), 2)
