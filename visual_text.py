from graph import open_files, graph_merge
import sys


def create_data(data):
    length = len(data[0])
    average_group_size = sum(list(map(len, data[0]))) / len(data[0])
    meetings_per_group = sum(data[1].values()) / len(data[1])

    average_attendance_per_egoid = []
    for egoid, groupsets in data[2].items():
        for group, attendance in groupsets.items():
            attendence_rates = list(map(lambda x: x / data[1][group], groupsets.values()))
            average_attendance_per_egoid.append(sum(attendence_rates) / len(attendence_rates))

    average_attendance = sum(average_attendance_per_egoid) / len(average_attendance_per_egoid)
    return length, average_group_size, meetings_per_group, average_attendance


if __name__ == '__main__':
    comm, basic, network = open_files(int(sys.argv[1]))

    data = graph_merge(comm, 3, 0.5, 3)
    results = create_data(data)
    output_string = \
        """
    Number of Groups: {}
    Average Group Size: {:.4f} 
    Meetings Per Group: {:.4f}
    Average Person Attendance: {:.4f}
    """.format(results[0], results[1], results[2], results[3])

    output_file = open("basic_stat_analysis.txt", "w")
    output_file.write(output_string)
    output_file.close()
