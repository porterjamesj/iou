
import json
import itertools as it

class DebtGraph:
    """
    A class to represent a directed graph of debts from one person to
    another. Each DebtGraph has a property graph (the in-memory
    representation of the graph), and methods for operating on
    it. graph is a dictonary of dictionaries; It can be thought of as
    graph[creditor][debtor].
    """
    def __init__(self,init):
        """
        Initialization method for a DebtGraph. If init is a list, it
        is interpreted as a list of names and an empty dept graph is
        constructed from them. If it is a string, it is interpreted as
        a filename, and the file (json format) is interpreted as a
        dict of dicts and used to initialize the object. If it is a dict,
        then this is assumed to be the graph for the new instances.
        """
        if isinstance(init,(list,tuple)):
            self.graph = {person:{} for person in init}
        elif isinstance(init,str):
            with open(init,"r") as fp:
                self.graph = json.load(fp)
        elif isinstance(init,dict):
            self.graph = init.copy()
        else:
            raise TypeError("Initialization must be from string, list, or dict.")

    def __repr__(self):
        """Representation of a DebtGraph."""
        return str(self.graph)

    def serialize(self,filename):
        """Serializes the graph to the named file as json."""
        with open(filename,"w") as fp:
            json.dump(self.graph,fp)

    def deserialize(self,filename):
        """
        Replaces the current graph with one read from the filename
        (json format) given.
        """
        with open(filename,"r") as fp:
            self.graph = json.load(fp)

    def remove(self,creditor,debtor,amount):
        """
        Wipe out amount of debtor's debt to creditor. If the debt
        would go negative, keep it at zero.
        """
        try:
            self.graph[creditor][debtor] -= amount
            if self.graph[creditor][debtor] < 0:
                del self.graph[creditor][debtor]
        except:
            raise KeyError("The specified debt does not exist.")

    def forgive(self,creditor,debtor):
        """Forgive the entire debt specified."""
        try:
            del self.graph[creditor][debtor]
        except:
            raise KeyError("The specified debt does not exist.")

    def add(self,creditor,debtors,amount):
        """
        Split an amount of debt to the specified creditor between all
        parties in the debtors list.
        """
        if isinstance(debtors,list):
            # check that all the debtors actually exist
            for debtor in debtors:
                if debtor not in self.graph.keys():
                    raise KeyError("debtor '{0}' not found.".format(debtor))
            # go ahead and add split / add the debt
            each_amount = float(amount) / len(debtors)
            for debtor in debtors:
                if debtor != creditor:
                    """
                    The above line is confusing, it is there to ensure
                    that splits in which one person buys something for a
                    group that includes them (and therefore is both a
                    debtor and the creditor) work correctly.
                    """
                    if debtor in self.graph[creditor]:
                        self.graph[creditor][debtor] += each_amount
                    else:
                        self.graph[creditor][debtor] = each_amount
        elif isinstance(debtors,(str,unicode,int)):
            # check that the debtor exists
            if debtors not in self.graph.keys():
                raise KeyError("debtor(s) '{0}' not found.".format(debtors))
            if debtors in self.graph[creditor]:
                self.graph[creditor][debtors] += float(amount)
            else:
                self.graph[creditor][debtors] = float(amount)
        else:
            raise TypeError("debtors must be either a list or string.")

    def cancel(self):
        """
        Cancels useless debt in symmetric relationships. For example,
        if A owes B $10 and B owes A $3, running cancel will cause A
        to simply owe B $7.
        """
        for person1 in self.graph.keys():
            for person2 in self.graph[person1].keys():
                if (person1 in self.graph[person2] and
                    self.graph[person1][person2] > 0 and
                    self.graph[person2][person1] > 0):
                    newdebt = (self.graph[person1][person2] -
                               self.graph[person2][person1])
                    if newdebt > 0:
                        self.graph[person1][person2] = newdebt
                        del self.graph[person2][person1]
                    else:
                        self.graph[person2][person1] = -newdebt
                        del self.graph[person1][person2]

    def __get_nodes(self):
        nodeflows = {person : 0.0 for person in self.graph}
        for person1 in self.graph:
            for person2 in self.graph[person1]:
                value = self.graph[person1][person2]
                nodeflows[person1] += value
                nodeflows[person2] -= value
        return nodeflows

    def __subgraphs(self,nodeset,n):
        """ Recursive function that returns a list of subsets covering the
        given nodeset. Guarantees that the number of subsets is maximized
        (i.e. that all possible subgraphs are broken out). The public
        find_subgraphs method is a wrapper around this."""
        print nodeset,n

        subsets = it.combinations(nodeset,n)
        for subset in subsets:
            if sum([node[1] for node in subset]) == 0.0:
                # this is a zero-sum subset, recurse
                print set(subset)
                return [set(subset)].extend(
                    self.__subgraphs(nodeset.difference(set(subset)), n))
        # if we don't find any zero-sum subsets, first check if we are done
        if n >= len(self.graph.keys())/2: # i don't like relying on this
            print nodeset
            return nodeset # we are done
        else:
            return self.__subgraphs(nodeset,n+1)

    def find_subgraphs(self):
        """Returns a list containing disconnected subgraphs of the overall
        graph."""
        nodeflows = self.__get_nodes() # dict of names => flows
        # as a preprocessing step, filter everyone with no net flow.
        nodeflows = [node for node in nodeflows if node[1] != 0.0]
        nodeset = set(nodeflows.items()) # set of (name, flow) tuples
        return self.__subgraphs(nodeset,2)

    def collapse(self):
        """
        Simplifies a graph with n nodes into n-1 edges. This is the best
        we can do for connected graphs, but will fail on graphs with
        disconnected subgraphs.
        """
        # First we compute the "flow" of money into or out of each node
        nodeflows = self.__get_nodes()
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
        try:
            del self.graph[person]
            for node in self.graph:
                if person in self.graph[node]:
                    del self.graph[node][person]
        except:
            raise KeyError("No such person in graph.")

    def rename_person(self,oldname,newname):
        """Change a person's name."""
        try:
            self.graph[newname] = self.graph[oldname]
            for node in self.graph:
                if oldname in self.graph[node]:
                    self.graph[node][newname] = self.graph[node][oldname]
                    del self.graph[node][oldname]
            del self.graph[oldname]
        except:
            raise KeyError("No such person in graph.")
