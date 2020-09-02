import networkx as nx
import pandas as pd
from GraphClasses import CommEvent, idNode
from pandas_load import open_files
from math import floor

"""
NOTE: This file is depreciated. This is merely here for archiving
"""


def create_graph(slice):
    """Creates Networkx undirected graph of communication events of a given slice"""
    graph = nx.Graph()
    for index, row in slice.iterrows():
        ego_node = idNode(row["egoid"], "Ego")
        alter_node = idNode(row["alterid"], "Alter")

        if ego_node.id not in graph:
            graph.add_node(ego_node.id, data=ego_node)

        if 10000 <= alter_node.id <= 99999:
            if alter_node not in graph:
                graph.add_node(alter_node.id, data=alter_node)

            comm_event = CommEvent(row["egoid"], row["alterid"], row["epochtime"])
            graph.add_edge(ego_node.id, alter_node.id, event=comm_event)
    return graph


def get_snapshots(slice):
    """Divide communication data into date sets"""
    datetime = slice["date"] + ' ' + slice["time"]
    slice["datetime"] = datetime
    slice = slice.set_index("datetime")

    start_date = (slice[:1]["date"] + ' ' + slice[:1]["time"]).to_list()[0]
    end_date = (slice[-1:]["date"] + ' ' + slice[-1:]["time"]).to_list()[0]

    dates = pd.date_range(start_date, end_date, freq='D').to_list()
    if end_date not in dates:
        dates.append(end_date)
    for i in range(len(dates) - 1):
        yield slice[str(dates[i]):str(dates[i + 1])]


def generate_lifetime_group_table(groupset, table, compare_table, mergedSet=None, exist=False):
    """Create Group Lifetime Table"""
    if mergedSet:
        set_to_add = mergedSet
    else:
        set_to_add = groupset
    for egoid in set_to_add:
        if egoid in compare_table and set_to_add in compare_table[egoid]:
            value = compare_table[egoid][set_to_add]
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
    for i in range(len(time_1)):
        for j in range(len(time_2)):
            member_set_i = get_member_set(time_1[i], time_1_meetings, time_1_lifetime_table, meetings_fraction)
            member_set_j = get_member_set(time_2[j], time_2_meetings, time_2_lifetime_table, meetings_fraction)
            if len(time_1[i].symmetric_difference(time_2[j])) <= merge_threshold \
                    and (not meetings_fraction or len(member_set_i.symmetric_difference(member_set_j)) <= merge_threshold):

                group = time_1[i].union(time_2[j])
                merged_groups.append(group)
                result_meeting[group] = time_1_meetings[time_1[i]] + 1
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
            result.append(time_2[j])
            result_meeting[time_2[j]] = time_2_meetings[time_2[j]]

            result_lifetime_table = generate_lifetime_group_table(time_2[j], result_lifetime_table,
                                                                  time_2_lifetime_table, exist=True)

    result.extend(merged_groups)
    return result, result_meeting, result_lifetime_table


def graph_merge(comm, merge_threshold, meeting_fraction, time_to_meeting_fraction):
    """Graph merging driver function"""
    gs = get_snapshots(comm)
    t_1 = next(gs)
    g1 = create_graph(t_1)
    initial_groups = [group for group in nx.connected_components(g1) if len(group) > 2]
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
        scc = [group for group in nx.connected_components(g) if len(group) > 2]
        scc = list(map(frozenset, scc))
        scc_meeting = {group: 1 for group in scc}

        scc_group_lifetime_table = {}
        for group in scc:
            scc_group_lifetime_table = generate_lifetime_group_table(group, scc_group_lifetime_table, {})

        # print(prev_groups_meeting)
        result_groups, result_group_meetings, result_group_lifetime_table = merge_algo(prev_groups,
                                                                                       prev_groups_meeting,
                                                                                       prev_group_lifetime_table,
                                                                                       scc, scc_meeting,
                                                                                       scc_group_lifetime_table,
                                                                                       merge_threshold,
                                                                                       meeting_fraction *
                                                                                       floor(t_i_counter // time_to_meeting_fraction))
        prev_groups = result_groups
        prev_groups_meeting = result_group_meetings
        prev_group_lifetime_table = result_group_lifetime_table
        t_i_counter += 1

        results.append((result_groups, result_group_meetings, result_group_lifetime_table))
    return results[-1]


if __name__ == '__main__':
    NUM_RECORDS = 400000
    network, basic, comm = open_files(NUM_RECORDS)
    result = graph_merge(comm, 3, 0.5, 1)
    print(result[1])
