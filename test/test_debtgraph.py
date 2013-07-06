from debtgraph import DebtGraph
from nose.tools import raises

class TestInit():
    """Initialization should occur properly."""
    def test_string_init(self):
        """Should correctly initialize a graph from a list of names."""
        dg = DebtGraph(["a","b","c"])
        assert dg.graph == {"a": {},"b": {},"c": {}}

    def test_dict_init(self):
        """Should correctly initialize a graph from a dictionary."""
        dg = DebtGraph({"a":{"b":20},"b":{}})
        assert dg.graph == {"a":{"b":20},"b":{}}

class TestManipulation():
    """Graph manipulation methods should work properly."""
    @classmethod
    def setUp(self):
        """Set up a test DebtGraph."""
        self.dg = DebtGraph(
            {"alice": {"bob": 20, "charlie":5},
             "bob": {"alice":10},
             "charlie": {}})

    #removal

    def test_remove_normal(self):
        """Should remove debt correctly."""
        self.dg.remove("alice","bob",5)
        assert self.dg.graph == {"alice": {"bob": 15, "charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {}}

    def test_remove_deletion(self):
        """Should delete the node if more debt is removed than exists."""
        self.dg.remove("alice","bob",25)
        assert self.dg.graph == {"alice": {"charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {}}

    @raises(KeyError)
    def test_remove_error(self):
        """Should throw an error when trying to remove a nonexistant debt."""
        self.dg.remove("charlie","bob",4)

    #forgiveness

    def test_forgive_normal(self):
        """Forgive method should delete debts."""
        self.dg.forgive("bob","alice")
        assert self.dg.graph == {"alice": {"bob": 20, "charlie":5},
                                 "bob": {},
                                 "charlie": {}}

    @raises(KeyError)
    def test_forgive_error(self):
        """Forgive method should throw an error when used on a nonexistant debt."""
        self.dg.forgive("bob","charlie")

    # addition

    def test_addition_normal(self):
        """Adding to an already existing debt should increase it."""
        self.dg.add("alice","bob",5)
        assert self.dg.graph == {"alice": {"bob": 25, "charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {}}

    def test_addition_split(self):
        """Adding a debt with multiple debtors should split the debt."""
        self.dg.add("charlie",["alice","bob"],10)
        assert self.dg.graph == {"alice": {"bob": 20, "charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {"alice":5,"bob":5}}

    def test_addition_split_self(self):
        """Adding a debt with multiple debtors including the creditor should
        spilt the debt between everyone except the creditor."""
        self.dg.add("charlie",["charlie","alice","bob"],15)
        assert self.dg.graph == {"alice": {"bob": 20, "charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {"alice":5,"bob":5}}

    @raises(TypeError)
    def test_addition_error(self):
        """Addition should throw an error if not called using a list or a
        string."""
        self.dg.add("alice",3,3)

    #cancellation

    def test_cancel(self):
        """Canceling useless debts should produce the correct graph."""
        self.dg.cancel()
        print self.dg.graph
        assert self.dg.graph == {"alice": {"bob": 10, "charlie":5},
                                 "bob": {},
                                 "charlie": {}}


class TestCollapse():
    """This has its own class becuase the setup is different."""

    @classmethod
    def setUp(self):
        self.dg = DebtGraph({"alice": {"charlie":5},
             "bob": {"alice":10},
             "charlie": {"bob":10}})

    def test_collapse(self):
        """Collapsing the graph should work as intended."""
        self.dg.collapse()
        assert self.dg.graph == {'charlie': {'alice': 5.0},
                                 'bob': {},
                                 'alice': {}}

class TestEdit():
    """Testing functions that manipulate the list of people in the graph."""

    @classmethod
    def setUp(self):
        """Set up a test DebtGraph."""
        self.dg = DebtGraph(
            {"alice": {"bob": 20, "charlie":5},
             "bob": {"alice":10},
             "charlie": {}})

    def test_add_person(self):
        """Should add a person to the graph correctly."""
        self.dg.add_person("danielle")
        assert self.dg.graph == {"alice": {"bob": 20, "charlie":5},
                                 "bob": {"alice":10},
                                 "charlie": {},
                                 "danielle":{}}

    def test_remove_person_normal(self):
        """Should remove a person and all their debts correctly."""
        self.dg.remove_person("alice")
        assert self.dg.graph == {"bob": {},
                                 "charlie": {}}

    @raises(KeyError)
    def test_remove_person_error(self):
        """Remove person should raise an error if the person does not exist."""
        self.dg.remove_person("zack")


    def test_rename_person_normal(self):
        """Should rename a person correctly when they exist."""
        self.dg.rename_person("alice","alex")
        assert self.dg.graph == {"alex": {"bob": 20, "charlie":5},
                                 "bob": {"alex":10},
                                 "charlie": {}}

    @raises(KeyError)
    def test_rename_person_error(self):
        """Rename person should throw an error if the person does not exist."""
        self.dg.rename_person("zack","anthony")
