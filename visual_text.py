from graph import open_files, graph_merge
import sys
import numpy as np


def create_data(data):
    length = len(data[0])
    average_group_size = sum(list(map(len, data[0]))) / len(data[0])
    meetings_per_group = sum(data[1].values()) / len(data[1])

    average_attendance_per_egoid = []
    for egoid, groupsets in data[2].items():
        attendance_rates = []
        for group, attendance in groupsets.items():
            assert attendance <= data[1][group]
            print("({0:}) / ({1:})".format(attendance, data[1][group]))
            attendance_rates.append(attendance / data[1][group])
        average_attendance_per_egoid.append(sum(attendance_rates) / len(attendance_rates))

    average_attendance = sum(average_attendance_per_egoid) / len(average_attendance_per_egoid)
    return length, average_group_size, meetings_per_group, average_attendance, average_attendance_per_egoid


if __name__ == '__main__':
    files = {
        "Comm": sys.argv[1],
        "Basic": sys.argv[2],
        "Network": sys.argv[3]
    }
    m_thresh = 1
    m_ratio = 0.5
    time_to_m = 3

    comm, basic, network = open_files(files, int(sys.argv[4]))
    output_file = open("1hr.txt", "w")

    # NOTE: Keep this Comment Here! This a separate test function for this file
    # print("Begin Analysis")
    # for i in range(1, 4):
    #     data = graph_merge(comm, i, 0.5, 3)
    #     results = create_data(data)
    #     output_string = \
    #         """
    #         {}, {}, {}
    #     Number of Groups: {}
    #     Average Group Size: {:.4f}
    #     Meetings Per Group: {:.4f}
    #     Average Person Attendance: {:.4f} ({:.4f} / {:.4f})\n
    #     """.format(i, m_ratio, time_to_m, results[0], results[1], results[2], results[3], sum(results[4]), len(results[4]))
    #     output_file.write(output_string)
    # output_file.flush()

    print("Begin Analysis")
    m_ratio_values = np.linspace(0.5, 0.9, 5)
    for j in m_ratio_values:
        data = graph_merge(comm, 1, j, 2)
        results = create_data(data)
        output_string = \
            """
            {}, {}, {}
        Number of Groups: {}
        Average Group Size: {:.4f}
        Meetings Per Group: {:.4f}
        Average Person Attendance: {:.4f} ({:.4f} / {:.4f} )\n
        """.format(m_thresh, j, time_to_m, results[0], results[1], results[2], results[3], sum(results[4]), len(results[4]))
        output_file.write(output_string)
        output_file.flush()
    output_file.close()
