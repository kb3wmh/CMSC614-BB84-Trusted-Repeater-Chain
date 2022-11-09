from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumProgram
from netsquid.components.instructions import INSTR_MEASURE,INSTR_MEASURE_X
import netsquid as ns

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import Random_basis_gen,Compare_basis

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

from util import BB84_CompareBasis


'''
To add value -1 on tarList at positions given by lossList.
input:
    lossList: A list indecates positions to add -1. (list of int)
    tarList: List to add -1. (list of any)
output:
    tarList: target List.(list of any)
'''
def AddLossCase(lossList,tarList):
    for i in range(len(lossList)):
        tarList.insert(lossList[i],-1)
    return tarList












'''
input:
    Pg: A quantum program (QuantumProgram)
output:
    resList: A list of outputs from the given quantum program, 
    also sorted by key.(list of int)
'''
class QG_B_measure(QuantumProgram):
    def __init__(self,basisList,num_bits):
        self.basisList=basisList
        self.num_bits=num_bits
        super().__init__()


    def program(self):   
        if len(self.basisList)!=self.num_bits:
            mylogger.error("B measurement error! List length did not match! \n")

        else:
            for i in range(len(self.basisList)):
                if self.basisList[i] == 0:                  # standard basis
                    self.apply(INSTR_MEASURE, 
                        qubit_indices=i, output_key=str(i),physical=True) 
                else:                              # 1 case # Hadamard basis
                    self.apply(INSTR_MEASURE_X, 
                        qubit_indices=i, output_key=str(i),physical=True) 
        
        yield self.run(parallel=False)



class BobProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,
                port_names=["portQB_1","portCB_1","portCB_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.qList=None
        self.loc_measRes=[]   
        self.basisList=Random_basis_gen(self.num_bits)
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1] #to
        self.portNameC2=port_names[2] #from

        self.key=[]
        self.endTime=None

    # =======================================B run ============================
    def run(self):
        
        qubitList=[]
        
        #receive qubits from A
        
        port = self.node.ports[self.portNameQ1]
        yield self.await_port_input(port)
        qubitList.append(port.rx_input().items)
        #mylogger.debug("B received qubits:{}\n".format(qubitList))
        
        
        #put qubits into B memory
        for qubit in qubitList:
            self.processor.put(qubit)
        
        self.myQG_B_measure=QG_B_measure(basisList=self.basisList,num_bits=self.num_bits)
        self.processor.execute_program(self.myQG_B_measure,qubit_mapping=[i for  i in range(self.num_bits)])
        
        yield self.await_program(processor=self.processor)


        
        # get meas result
        for i in range(self.num_bits):
            tmp=self.myQG_B_measure.output[str(i)][0]
            self.loc_measRes.append(tmp)
        
        mylogger.debug("B meas res:{}\n".format(self.loc_measRes))

        
        # self.B_send_basis()
        self.node.ports[self.portNameC1].tx_output(self.basisList)
        
        # receive A's basisList
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        basis_A=port.rx_input().items
        mylogger.debug("B received basis_A:{}\n".format(basis_A))

        
        self.key=BB84_CompareBasis(self.basisList,basis_A,self.loc_measRes)
        
        mylogger.debug("B key:{}\n".format(self.key))

        self.endTime=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)


        '''
        # send matchB
        self.node.ports[self.portNameC1].tx_output(matchB)

        # receive matchA
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        matchA=port.rx_input().items
        mylogger.debug("B received matchA:{}\n".format(matchA))


        
        for n,item in enumerate(matchB):
            self.key.append(matchA[n]^item) #XOR

        self.key=''.join(map(str, self.loc_measRes))
        mylogger.debug("B keys:{}\n".format(self.key))
        #print("B key:",self.key)
        '''


        

        

