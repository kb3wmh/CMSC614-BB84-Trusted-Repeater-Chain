class QNode:
    def __init__(self, compromised=False):
        self.compromised = compromised


    def isCompromised(self):
        return self.compromised
