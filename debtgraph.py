import json

class DebtGraph:
    """
    A class to represent a directed graph of debts from one person to
    another. Each DebtGraph has a property graph (the in-memory
    representation of the graph), and methods for operating on
    it. graph is a dictonary of dictionaries; It can be thought of as
    graph[creditor][debtor].
    """
    def __init__(self,people):
        """
        Initialization method for a DebtGraph. If people is a list, it
        is interpreted as a list of names and an empty dept graph is
        constructed from them. If it is a string, it is interpreted as
        a filename, and the file (json format) is interpreted as a
        dict of dicts and used to initialize the object.
        """
        if type(people) is list or type(people) is tuple:
            self.graph = {}
            for person1 in people:
                self.graph[person1] = {}
        elif type(people) is str:
            fp = open(people,"r")
            self.graph = json.load(fp)
            fp.close()
        else:
            raise TypeError("Initialization must be from string or list.")

    def __repr__(self):
        """Representation of a DebtGraph."""
        return str(self.graph)
        
    def serialize(self,filename):
        """Serializes the graph to the named file as json."""
        fp = open(filename,"w")
        json.dump(self.graph,fp)
        fp.close()

    def deserialize(self,filename):
        """
        Replaces the current graph with one read from the filename
        (json format) given.
        """
        fp = open(filename,"r")
        self.graph = json.load(fp)
        fp.close()

    def add(self,creditor,debtor,amount):
        """
        Add a debt from `debtor` to `creditor` in the amount
        specified.
        """
        if debtor in self.graph[creditor]:
            self.graph[creditor][debtor] += float(amount)
        else:
            self.graph[creditor][debtor] = float(amount)

    def remove(self,creditor,debtor,amount):
        """
        Wipe out amount of debtor's debt to creditor. If the debt
        would go negative, keep it at zero.
        """
        if debtor in self.graph[creditor]:
            self.graph[creditor][debtor] -= amount
            if self.graph[creditor][debtor] < 0:
                del self.graph[creditor][debtor]
        else:
            # should this fail silently or raise an error?
            raise KeyError("The specified debt does not exist.")

    def forgive(self,creditor,debtor):
        """Forgive the entire debt specified."""
        if debtor in self.graph[creditor]:
            del self.graph[creditor][debtor]
        else:
            # should an error be raised here?
            pass

    def split(self,creditor,debtors,amount):
        """
        Split an amount of debt to the specified creditor between all
        parties in the debtors list.
        """
        each_amount = amount / len(debtors)
        for debtor in debtors:
            if debtor != creditor:
                """
                The above line is confusing, it is there to ensure
                that splits in which one person buys something for a
                group that includes them (and therefore is both a
                debtor and the creditor) work correctly.
                """
                self.add(creditor,debtor,each_amount)

    def cancel(self):
        """
        Cancels useless debt in symmetric relationships. For example,
        if A owes B $10 and B owes A $3, running cancel will cause A
        to simply owe B $7.
        """
        for person1 in self.graph:
            for person2 in self.graph[person1]:
                if (person1 in self.graph[person2] and
                    self.graph[person1][person2] > 0 and
                    self.graph[person2][person1] > 0):
                    newdebt = (self.graph[person1][person2] -
                               self.graph[person2][person1])
                    if newdebt > 0:
                        self.graph[person1][person2] = newdebt
                        self.graph[person2][person1] = 0.0
                    else:
                        self.graph[person2][person1] = -newdebt
                        self.graph[person1][person2] = 0.0

    def collapse(self):
        """
        Collapses the debt graph to remove all useless
        edges. See complete documentation for more details.
        """
        # First we compute the "flow" of money into or out of each node
        nodeflows = {person : 0.0 for person in self.graph}
        for person1 in self.graph:
            for person2 in self.graph[person1]:
                value = self.graph[person1][person2]
                nodeflows[person1] += value
                nodeflows[person2] -= value
        # Now split into positive and negative and sort each
        pos_flows = [list(flow) for flow in nodeflows.items() if flow[1] > 0]
        neg_flows = [list(flow) for flow in nodeflows.items() if flow[1] < 0]
        pos_flows.sort(key = lambda t: -t[1])
        neg_flows.sort(key = lambda t: t[1])
        # Now come up with the new optimal debt graph
        self.__init__(nodeflows.keys())
        while pos_flows and neg_flows:
            credit = pos_flows[0][1]
            debit = neg_flows[0][1]
            creditor = pos_flows[0][0]
            debtor = neg_flows[0][0]
            # conditional says keep going until both are empty
            if abs(credit) == abs(debit):
                self.add(creditor,debtor,credit)
                neg_flows.pop(0)
                pos_flows.pop(0)
            if abs(credit) < abs(debit):
                self.add(creditor,debtor,credit)
                pos_flows.pop(0)
                neg_flows[0][1] += credit
            if abs(credit) > abs(debit):
                self.add(creditor,debtor,abs(debit))
                neg_flows.pop(0)
                pos_flows[0][1] += debit

    def cleanup(self):
        """Convenience function to run cancel and collapse at once."""
        self.cancel()
        self.collapse()
        
    def add_person(self,person):
        """Add a new person (potential node)."""
        self.graph[person] = {}

    def remove_person(self,person):
        """Remove a person and all their associated debts."""
        if person in self.graph:
            del self.graph[person]
            for node in self.graph:
                if person in self.graph[node]:
                    del self.graph[node][person]
        else:
            raise KeyError("No such person in graph.")
