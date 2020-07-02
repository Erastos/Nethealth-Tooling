# Networkx Edge Data - Communication Event Class
class CommEvent:
    def __init__(self, egoid, alterid, timestamp):
        self.egoid = egoid
        self.alterid = alterid
        self.timestamp = timestamp

    def __str__(self):
        return "Ego: {} -> Alter: {}".format(self.egoid, self.alterid)

    def __repr__(self):
        return self.__str__()


# Networkx Node Data - General ID Class that represents individuals in the communication data
class idNode:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.lifetime = -1

    def __str__(self):
        return "ID ({}): {}".format(self.type, self.id)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id
