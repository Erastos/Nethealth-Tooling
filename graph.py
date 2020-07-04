import networkx as nx
import pandas as pd
from GraphClasses import CommEvent, idNode
from pandas_load import open_files


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


def naive_merging(time_1, time_2, merge_threshold):
    """Merge graph connected components if the difference between the sets is below a threshold. Add all other components to a result set"""
    merged_groups = []
    for i in range(len(time_1)):
        for j in range(len(time_2)):
            if len(time_1[i].symmetric_difference(time_2[j])) < merge_threshold:
                merged_groups.append(time_1[i].union(time_2[j]))
                break
    result = []
    for i in range(len(time_1)):
        is_subset = False
        for j in range(len(merged_groups)):
            if time_1[i].issubset(merged_groups[j]):
                is_subset = True
                break
        if not is_subset:
            result.append(time_1[i])

    for j in range(len(time_2)):
        is_subset = False
        for k in range(len(merged_groups)):
            if time_2[j].issubset(merged_groups[k]):
                is_subset = True
                break
        if not is_subset:
            result.append(time_2[j])
    result.extend(merged_groups)
    return result


def graph_merge(comm):
    """Graph merging driver function"""
    gs = get_snapshots(comm)
    t_1 = next(gs)
    g1 = create_graph(t_1)
    initial_groups = [group for group in nx.connected_components(g1) if len(group) > 2]
    prev_groups = initial_groups
    for t_i in gs:
        g = create_graph(t_i)
        scc = [group for group in nx.connected_components(g) if len(group) > 2]
        result_groups = naive_merging(prev_groups, scc, 3)
        prev_groups = result_groups


if __name__ == '__main__':
    NUM_RECORDS = 200000
    network, basic, comm = open_files(NUM_RECORDS)
    graph_merge(comm)