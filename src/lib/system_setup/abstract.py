class Abstract(object):
    def __init__(self, facts):
        self.facts = facts

    def configure(self):
        raise NotImplementedError("Should have implemented this")

    def install_monitoring(self):
        raise NotImplementedError("Should have implemented this")
