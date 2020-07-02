import csv

"""
NOTE: This file is outdated. Use pandas_loader instead. This file is here for documentation purposes
"""

FILE_NAME = "/home/erastos/Downloads/NetHealth Data/CommEvents(2-28-20)_study_start.csv"


# Loads Data From File using a generator
def load_data(filename, start_date="2015-08-16"):
    """Loads Data From File using a generator"""
    file = open(filename, 'r', buffering=1)
    reader = csv.reader(file)
    headers = next(reader)
    yield headers

    # Seeks forward to desired date
    for i, row in enumerate(reader):
        if row[headers.index('date')] == start_date:
            break
    for row in reader:
        yield row


def retrieve_ego_data(data_generator, header_list, num_records, egoId):
    """Gets messages equal to a certain ego id"""
    for i in range(num_records):
        row = next(data_generator)
        if int(row[header_list.index("egoid")]) == egoId or egoId == -1:
            yield row


def retrieve_ego_demos(demo, demo_value=None):
    """Get the egoIds that have a specific value for a specific demographic"""
    basic_survey_file = open("/home/erastos/Downloads/NetHealth Data/BasicSurvey(3-6-20).csv")
    reader = csv.reader(basic_survey_file)
    headers: list = next(reader)
    egoIds = []
    for row in reader:
        if row[headers.index(demo)] != '':
            if demo_value is None or row[headers.index(demo)] == demo_value:
                egoIds.append(int(row[headers.index("egoid")]))
    return egoIds


def check_demo_social_network(demo, demo_value):
    """Check how many of the egoids with the same demo value communicate with one another"""
    hit_counter = 0
    egoIds = retrieve_ego_demos(demo, demo_value)
    for egoID in egoIds:
        dg = load_data(FILE_NAME)
        headers = next(dg)
        red = retrieve_ego_data(dg, headers, 25000 * 10, int(egoID))
        for row in red:
            if int(row[headers.index("alterid")]) in egoIds:
                print("Hit!")
                hit_counter += 1
                break
        print("Done with {}".format(egoID))
    print(egoIds)
    print("Hit Counter: {:.2%} ({:d} / {:d})".format(hit_counter / len(egoIds), hit_counter, len(egoIds)))


def retrieve_ego_network_survey(egoid):
    """Get the alterids in a egoid's network as outlines by the network survey"""
    network_survey_file = open("/home/erastos/Downloads/NetHealth Data/NetWorkSurvey(2-28-20).csv")
    reader = csv.reader(network_survey_file)
    headers: list = next(reader)
    alterIds = []
    for row in reader:
        if int(row[headers.index("egoid")]) == egoid:
            alterIds.append(int(row[headers.index("alterid")]))
    print(alterIds)
    return alterIds


def retrieve_ego_network_comm(egoid, num_records):
    """Check if an egoid communicates with members in the network as described by the Network Survey """
    hit_counter = 0
    alterids = retrieve_ego_network_survey(egoid)
    for alterid in alterids:
        dg = load_data(FILE_NAME)
        headers = next(dg)
        red = retrieve_ego_data(dg, headers, num_records, int(alterid))
        for row in red:
            if int(row[headers.index("alterid")]) in alterids:
                print("Hit!")
                hit_counter += 1
                break
        print("Done with {}".format(alterid))
    print(alterids)
    print("Hit Counter: {:.2%} ({:d} / {:d})".format(hit_counter / len(alterids), hit_counter, len(alterids)))
    return hit_counter / len(alterids), hit_counter, len(alterids)


if __name__ == '__main__':
    # Testing code while performing analysis


    ld = load_data("/home/erastos/Downloads/NetHealth Data/CommEvents(2-28-20)_study_start.csv")
    header_list = next(ld)
    # reg = retrieve_ego_data(ld, header_list, 25000 * 20, 66642)
    # demo = retrieve_ego_demos("hs_1", "Private independent college-prep school")
    # check_demo_social_network("usedrugs_1", "Three times a week or more")

    network_survey_file = open("/home/erastos/Downloads/NetHealth Data/NetWorkSurvey(2-28-20).csv")
    reader = csv.reader(network_survey_file)
    headers = next(reader)
    results = []

    # Open Results File
    result_file = open("result_file.txt", "w")

    already_checked = set()
    for row in reader:
        print(row[0])
        if int(row[0]) not in already_checked:
            already_checked.add(int(row[0]))
            result = retrieve_ego_network_comm(int(row[0]), 25000 * 20)
            results.append(result)
            result_file.write("{}: {}\n".format(row[0], str(result)))

    # retrieve_ego_network_comm(66642, 25000 * 20)

    # for row in reg:
    #     print(row)
    # print(demo)
