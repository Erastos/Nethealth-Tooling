import matplotlib.pyplot as plt
from graph import graph_merge, open_files

plt.style.use('ggplot')


def get_group_numbers():
    num_records = 200000
    network, basic, comm = open_files(num_records)
    num_lengths = []
    # Run through merge thresholds
    for i in range(1, 11):
        result = graph_merge(comm, i)
        num_lengths.append(len(result))
        print("Finished with mthresh={}".format(i))
    plt.plot(list(range(1, 10)), num_lengths)
    plt.xlabel("Merge Threshold")
    plt.ylabel("Number of Groups")
    plt.title("Number of Groups vs Merge Threshold (n={})".format(num_records))
    plt.show()


get_group_numbers()
