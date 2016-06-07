class Abstract:
    def __init__(self):
        pass

    @staticmethod
    def getname():
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def discover(system):
        raise NotImplementedError("Should have implemented this")

    def configure(self, system):
        raise NotImplementedError("Should have implemented this")
