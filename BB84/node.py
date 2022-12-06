class QNode:
    def __init__(self, compromised=False):
        self.compromised = compromised


    def compromise(self):
        self.compromised = True
    
    def isCompromised(self):
        return self.compromised
