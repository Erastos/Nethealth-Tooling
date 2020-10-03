def remove_group(group, groupList, group_meetings, lifetime_data, removeEgoIds):
    # NOTE: This might be very inefficient
    for egoid in list(lifetime_data.keys()):
        for group_i in list(lifetime_data[egoid].keys()):
            if group_i == group:
                lifetime_data[egoid].pop(group_i)
                if removeEgoIds and len(lifetime_data[egoid]) == 0:
                    lifetime_data.pop(egoid)

    groupList.remove(group)
    del group_meetings[group]


def freq_filter_data(result_data, filter_time_amount, number_of_nodes):
    for i in range(len(result_data[0])):
        for j in range(len(result_data[0])):
            # NOTE: It appears that we have duplicates
            assert not (i != j and result_data[0][i] == result_data[0][j])

    groupList_copy = result_data[0].copy()
    for group in groupList_copy:
        if len(group) <= number_of_nodes and result_data[1][group] <= filter_time_amount:
            remove_group(group, result_data[0], result_data[1], result_data[2], False)


if __name__ == '__main__':
    # testGroup = frozenset([1, 2, 3, 4, 5])
    groupList = [frozenset([1, 2, 3, 4, 5]), frozenset([5, 6, 7, 8]), frozenset([9, 10, 11, 12]), frozenset([1, 2]), frozenset([3, 4])]
    groupMeetings = {groupList[0]: 1, groupList[1]: 2, groupList[2]: 3, groupList[3]: 1, groupList[4]: 1}
    lifetimeTable = {}
    for group in groupList:
        for egoid in group:
            if egoid not in lifetimeTable:
                lifetimeTable[egoid] = {group: 1}
            else:
                lifetimeTable[egoid][group] = 1
    data_result = [groupList, groupMeetings, lifetimeTable]

    freq_filter_data(data_result, 1, 2)
    print(groupList)
    print(groupMeetings)
    print(lifetimeTable)
