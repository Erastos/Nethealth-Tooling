from graph import open_files, graph_merge
import sys
import numpy as np


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
    files = {
        "Comm": sys.argv[1],
        "Basic": sys.argv[2],
        "Network": sys.argv[3]
    }
    comm, basic, network = open_files(files, int(sys.argv[4]))

    print("Begin Base Analysis")
    data = graph_merge(comm, 3, 0.5, 3)
    results = create_data(data)
    output_string = \
        """
        {}, {}, {}
    Number of Groups: {}
    Average Group Size: {:.4f} 
    Meetings Per Group: {:.4f}
    Average Person Attendance: {:.4f}
    """.format(3, 0.5, 3, results[0], results[1], results[2], results[3])

    min_group_size = results[1]

    m_thresh = 3
    meet_thresh = 0.5
    time_to_meet_thresh = 3

    output_file = open("basic_stat_analysis.txt", "w")
    for i in range(6):
        print("Beginning Analysis of m_thresh({}), meet_thresh({}). time_to_meet({})".format(i, meet_thresh,
                                                                                             time_to_meet_thresh))
        data = graph_merge(comm, i, meet_thresh, time_to_meet_thresh)
        results = create_data(data)
        if results[1] < min_group_size:
            min_group_size = results[1]
            m_thresh = i

        output_string = \
            """
            
            {}, {}, {}
        Number of Groups: {}
        Average Group Size: {:.4f} 
        Meetings Per Group: {:.4f}
        Average Person Attendance: {:.4f}
        """.format(i, meet_thresh, time_to_meet_thresh, results[0], results[1], results[2], results[3])

        output_file.write(output_string)
    print("Minimum Found: m_thresh({}), meet_thresh({}), time_to_meet({})".format(m_thresh, meet_thresh, time_to_meet_thresh))

    listMeetThresh = np.arange(0.1, 1.1, 0.1)
    for j in listMeetThresh:
        print("Beginning Analysis of m_thresh({}), meet_thresh({}). time_to_meet({})".format(m_thresh, j,
              time_to_meet_thresh))
        data = graph_merge(comm, m_thresh, j, time_to_meet_thresh)
        results = create_data(data)
        if results[1] < min_group_size:
            min_group_size = results[1]
            meet_thresh = j

        output_string = \
            """
            
            {}, {}, {}
        Number of Groups: {}
        Average Group Size: {:.4f} 
        Meetings Per Group: {:.4f}
        Average Person Attendance: {:.4f}
        """.format(m_thresh, j, time_to_meet_thresh, results[0], results[1], results[2], results[3])

        output_file.write(output_string)

    print("Minimum Found: m_thresh({}), meet_thresh({}), time_to_meet({})".format(m_thresh, meet_thresh, time_to_meet_thresh))

    for k in range(1, 10):
        print("Beginning Analysis of m_thresh({}), meet_thresh({}). time_to_meet({})".format(m_thresh, meet_thresh,
              k))
        data = graph_merge(comm, m_thresh, meet_thresh, k)
        results = create_data(data)
        if results[1] < min_group_size:
            min_group_size = results[1]
            time_to_meet_thresh = k

        output_string = \
            """
            
            {}, {}, {}
        Number of Groups: {}
        Average Group Size: {:.4f} 
        Meetings Per Group: {:.4f}
        Average Person Attendance: {:.4f}
        """.format(m_thresh, meet_thresh, k, results[0], results[1], results[2], results[3])


        output_file.write(output_string)

    print("Minimum Found: m_thresh({}), meet_thresh({}), time_to_meet({})".format(m_thresh, meet_thresh, time_to_meet_thresh))

    output_file.close()
