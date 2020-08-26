from GraphClasses import CommEvent, idNode
# from pandas_load import open_files, remove_outlier_data
from loader2 import open_files, Headers
from math import floor
import igraph
import datetime
import time
import sys


def create_graph(slice):
    """Creates Networkx undirected graph of communication events of a given slice"""
    graph = igraph.Graph()
    for row in slice:
        ego_node = idNode(int(row[Headers.EGOID.value]), "Ego")
        alter_node = idNode(int(row[Headers.ALTERID.value]), "Alter")

        if len(graph.vs) == 0 or ego_node.id not in list(graph.vs['name']):
            graph.add_vertex(ego_node.id)

        if 10000 <= alter_node.id <= 99999:
            if len(list(graph.vs)) == 0 or alter_node.id not in list(graph.vs['name']):
                graph.add_vertex(alter_node.id)

            # comm_event = CommEvent(row["egoid"], row["alterid"], row["epochtime"])
            graph.add_edge(graph.vs.select(lambda vertex: vertex['name'] == ego_node.id)[0],
                           graph.vs.select(lambda vertex: vertex['name'] == alter_node.id)[0])
    return graph


def get_date_range(start_date, end_date):
    """Get range of datetimes from start_date to end_date incremented by a timedelta"""
    start_datetime = datetime.datetime(*time.strptime(start_date, "%Y-%m-%d %H:%M:%S")[:6])
    end_datetime = datetime.datetime(*time.strptime(end_date, "%Y-%m-%d %H:%M:%S")[:6])

    time_delta = datetime.timedelta(hours=1)
    date_range = [start_datetime]
    while date_range[-1] < end_datetime:
        date_range.append(date_range[-1] + time_delta)
    if date_range[-1] > end_datetime:
        date_range.pop(-1)
    date_range.append(end_datetime)
    return date_range


def get_data_in_timeslice(start_index, comm, end_date):
    """Get all of the data in between a start index and an end_date"""
    results = []
    i = 0
    for i in range(start_index, len(comm)):
        date_string = comm[i][Headers.DATE.value] + ' ' + comm[i][Headers.TIME.value]
        date_datetime = datetime.datetime(*time.strptime(date_string, "%Y-%m-%d %H:%M:%S")[:6])
        if date_datetime > end_date:
            break

        results.append(comm[i])
    results.pop(-1)
    return results, i


def get_snapshots(slice):
    """Divide communication data into date sets"""

    start_date = slice[0][Headers.DATE.value] + ' ' + slice[0][Headers.TIME.value]
    end_date = slice[-1][Headers.DATE.value] + ' ' + slice[-1][Headers.TIME.value]

    # start_date = (slice[:1]["date"] + ' ' + slice[:1]["time"]).to_list()[0]
    # end_date = (slice[-1:]["date"] + ' ' + slice[-1:]["time"]).to_list()[0]

    date_range = get_date_range(start_date, end_date)
    index = 0
    for i in range(len(date_range) - 1):
        result, index = get_data_in_timeslice(index, slice, date_range[i + 1])
        print("{} -> {}".format(date_range[i], date_range[i + 1]))
        yield result

    # dates = pd.date_range(start_date, end_date, freq='D').to_list()
    # if end_date not in dates:
    #     dates.append(end_date)
    # for i in range(len(dates) - 1):
    #     print("{} -> {}".format(dates[i], dates[i + 1]))
    #     yield slice[str(dates[i]):str(dates[i + 1])]


def generate_lifetime_group_table(groupset, table, compare_table, mergedSet=None, exist=False):
    """Create Group Lifetime Table, a table which contains a egoids's attendance number per individual group"""
    if mergedSet:
        set_to_add = mergedSet
    else:
        set_to_add = groupset
    for egoid in set_to_add:
        if egoid in compare_table and set_to_add in compare_table[egoid]:
            value = compare_table[egoid][set_to_add]
            # NOTE: This appears to be where a bug is. Not sure if it is the one causing the assert errors
            if mergedSet and egoid in groupset:
                value += 1
        else:
            if exist:
                raise KeyError("This Key is Required to Exist {} - {}".format(egoid, set_to_add))
            value = 1

        if not egoid in table:
            table[egoid] = {set_to_add: value}
        else:
            table[egoid][set_to_add] = value

    return table


def get_member_set(groupset, group_meetings, lifetime_table, member_threshold):
    """Create a set including only a members groups"""
    if member_threshold == 0:
        return frozenset({-1})

    member_set = frozenset()
    for egoid in groupset:
        if egoid in lifetime_table and groupset in lifetime_table[egoid]:
            meetings = lifetime_table[egoid][groupset]
        else:
            meetings = 1
        if meetings / group_meetings[groupset] >= member_threshold:
            member_set = member_set.union(frozenset([egoid]))
    return member_set


def merge_algo(time_1, time_1_meetings, time_1_lifetime_table, time_2, time_2_meetings, time_2_lifetime_table,
               merge_threshold, meetings_fraction=0):
    """Merge graph connected components if the difference between the sets is below a threshold. Add all other components to a result set"""
    merged_groups = []
    result_meeting = {}
    result_lifetime_table = {}
    # Merge Components Above a Certain Threshold
    for i in range(len(time_1)):
        for j in range(len(time_2)):
            # Calculate Member Sets, sets containing people who attended meetings above a certain fraction (personal meetings/total group meetings)
            member_set_i = get_member_set(time_1[i], time_1_meetings, time_1_lifetime_table, meetings_fraction)
            member_set_j = get_member_set(time_2[j], time_2_meetings, time_2_lifetime_table, meetings_fraction)
            # Member Amount Criteria holds after a certain amount of time as set by Time to Meetings
            if len(time_1[i].symmetric_difference(time_2[j])) <= merge_threshold \
                    and (
                    not meetings_fraction or len(member_set_i.symmetric_difference(member_set_j)) <= merge_threshold):
                # NOTE: This might need to be member set's get merged (where applicable)
                group = time_1[i].union(time_2[j])
                # If a group is merged, then it means that it existed in the next time slice, meaning that it had another meeting (Assumption that could be wrong)
                merged_groups.append(group)
                # NOTE: This is the line that is causing the assert issues
                # result_meeting[group] = time_1_meetings[time_1[i]] + 1
                result_meeting[group] = time_1_meetings[group] + 1 if group in time_1_meetings else time_1_meetings[time_1[i]] + 1
                result_lifetime_table = generate_lifetime_group_table(time_2[j], result_lifetime_table,
                                                                      time_1_lifetime_table, group)
    result = []
    for i in range(len(time_1)):
        is_subset = False
        for j in range(len(merged_groups)):
            if time_1[i].issubset(merged_groups[j]):
                is_subset = True
                break
        if not is_subset:
            result.append(time_1[i])
            # Time 1 Group and Egoid Meeting Attendance are not incremented here, as time_1 is the combined results from all other previous time slices
            result_meeting[time_1[i]] = time_1_meetings[time_1[i]]

            result_lifetime_table = generate_lifetime_group_table(time_1[i], result_lifetime_table,
                                                                  time_1_lifetime_table, exist=True)

    for j in range(len(time_2)):
        is_subset = False
        for k in range(len(merged_groups)):
            if time_2[j].issubset(merged_groups[k]):
                is_subset = True
                break
        if not is_subset:
            # Time 2 Group and Egoid Meeting Attendence are not incremented here as this is created in the graph_merge function
            result.append(time_2[j])
            result_meeting[time_2[j]] = time_2_meetings[time_2[j]]

            result_lifetime_table = generate_lifetime_group_table(time_2[j], result_lifetime_table,
                                                                  time_2_lifetime_table, exist=True)

    result.extend(merged_groups)

    for egoid, groupsets in result_lifetime_table.items():
        for group, attendance in groupsets.items():
            assert attendance <= result_meeting[group]

    return result, result_meeting, result_lifetime_table


def graph_merge(comm, merge_threshold, meeting_fraction, time_to_meeting_fraction):
    """Graph merging driver function"""

    gs = get_snapshots(comm)

    # Initial Data Population
    t_1 = next(gs)
    g1 = create_graph(t_1)
    # Gets Collected Components of len greater than 2
    initial_groups = [{g1.vs[group[i]]['name'] for i in range(len(group))} for group in g1.clusters() if len(group) > 2]
    initial_groups = list(map(frozenset, initial_groups))
    initial_groups_meeting = {group: 1 for group in initial_groups}

    prev_groups = initial_groups
    prev_groups_meeting = initial_groups_meeting

    prev_group_lifetime_table = {}
    for group in prev_groups:
        prev_group_lifetime_table = generate_lifetime_group_table(group, prev_group_lifetime_table, {})

    results = []
    t_i_counter = 1
    for t_i in gs:
        g = create_graph(t_i)
        scc = [{g.vs[group[i]]['name'] for i in range(len(group))} for group in g.clusters() if len(group) > 2]
        scc = list(map(frozenset, scc))
        scc_meeting = {group: 1 for group in scc}

        scc_group_lifetime_table = {}
        for group in scc:
            scc_group_lifetime_table = generate_lifetime_group_table(group, scc_group_lifetime_table, {})

        result_groups, result_group_meetings, result_group_lifetime_table = merge_algo(prev_groups,
                                                                                       prev_groups_meeting,
                                                                                       prev_group_lifetime_table,
                                                                                       scc, scc_meeting,
                                                                                       scc_group_lifetime_table,
                                                                                       merge_threshold,
                                                                                       meeting_fraction *
                                                                                       floor(
                                                                                           t_i_counter // time_to_meeting_fraction))
        prev_groups = result_groups
        prev_groups_meeting = result_group_meetings
        prev_group_lifetime_table = result_group_lifetime_table
        t_i_counter += 1

        results.append((result_groups, result_group_meetings, result_group_lifetime_table))
    return results[-1]


if __name__ == '__main__':
    NUM_RECORDS = 200000
    files = {
        "Comm": sys.argv[1],
        "Basic": sys.argv[2],
        "Network": sys.argv[3]
    }
    comm, basic, network = open_files(files, NUM_RECORDS)
    result = graph_merge(comm, 3, 0.5, 1)
    print(result[1])

    get_snapshots(comm)
