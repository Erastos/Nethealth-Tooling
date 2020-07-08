import matplotlib.pyplot as plt
from graph import graph_merge, open_files

plt.style.use('ggplot')

num_records = 400000


def get_mthresh_data(merge_threshold):
    network, basic, comm = open_files(num_records)
    num_lengths = []
    # Run through merge thresholds
    for i in range(1, merge_threshold + 1):
        result = graph_merge(comm, i)
        num_lengths.append(result)
        print("Finished with mthresh={}".format(i))
    return num_lengths


def get_group_numbers(merge_threshold):
    mthresh_data = get_mthresh_data(merge_threshold)
    mthresh_data = list(map(lambda x: x[0], mthresh_data))
    num_lengths = map(len, mthresh_data)

    plt.plot(list(range(1, merge_threshold + 1)), list(num_lengths))
    plt.xlabel("Merge Threshold")
    plt.ylabel("Number of Groups")
    plt.title("Number of Groups vs Merge Threshold (n={})".format(num_records))
    plt.show()


def get_group_average(merge_threshold):
    mthresh_data = get_mthresh_data(merge_threshold)
    mthresh_data = list(map(lambda x: x[0], mthresh_data))
    averages = []
    for i in mthresh_data:
        group_lengths = list(map(len, i))
        averages.append(sum(group_lengths) // len(group_lengths))

    plt.plot(list(range(1, merge_threshold + 1)), averages)
    plt.xlabel("Merge Threshold")
    plt.ylabel("Avg Group Size")
    plt.title("Avg Group Size vs Merge Threshold (n={})".format(num_records))
    plt.show()


def get_meetings_per_group(merge_threshold):
    mthresh_data = get_mthresh_data(merge_threshold)
    meetings_per_group = []
    for i in mthresh_data:
        total_meetings = sum(i[1].values())
        meetings_per_group.append(total_meetings / len(i[0]))
    plt.plot(list(range(1, merge_threshold + 1)), meetings_per_group)
    plt.xlabel("Merge Threshold")
    plt.ylabel("Meetings per Group")
    plt.title("Meetings per Group vs Merge Threshold (n={})".format(num_records))
    plt.show()


# get_group_numbers(10)
# get_group_average(10)
get_meetings_per_group(10)
