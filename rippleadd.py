from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy


def storeValues(x, y):
    circuit = QuantumCircuit((len(x)*3)+1,len(x)+1)
    for i in range(len(x)):
        if x[::-1][i] == "1":
            circuit.x(i)
    for j in range(len(y)):
        if y[::-1][j] == "1":
            circuit.x(len(x)+j)
    return circuit


def fullAdder(input1, input2, carryin, carryout, circuit):
    circuit.ccx(input1, input2, carryout)
    circuit.cx(input1, input2)
    circuit.ccx(input2, carryin, carryout)
    circuit.cx(input2, carryin)
    circuit.cx(input1, input2)


def rippleAdder(val1: int, val2: int, draw: bool = False, simulate: bool = True) -> int:
    x = bin(val1)[2:]
    y = bin(val2)[2:]
    if len(x) > len(y):
        while len(y) != len(x):
            y = "0" + y
    else:
        while len(x) != len(y):
            x = "0" + x
    circuit = storeValues(x, y)
    for i in range(len(x)):
        fullAdder(i, len(x)+i, len(x)+len(y)+i, len(x)+len(y)+i+1, circuit)
        circuit.barrier()

    for i in range(len(x)+1):
        circuit.measure([(len(x)*2)+i], [i])
    
    if simulate:
        simulator = Aer.get_backend("qasm_simulator")
        result = execute(circuit, backend=simulator, shots=1).result()
    else:
        provider = IBMQ.load_account()
        backend = least_busy(IBMQ.backends())
        job = execute(circuit, backend=backend, shots=1)
        job_monitor(job)
        result = job.result()

    if draw:
        circuit.draw()
    
    return int(list(result.get_counts().keys())[0], 2)


if __name__ == "__main__":
    value1 = int(input('Enter an integer '))
    value2 = int(input('Enter the second Integer '))
    drawCircuit = bool(input("Draw a circuit?(True/False) "))
    simul = bool(input("use a simulator? (True/False) "))
    print(f"{value1}+{value2} = {rippleAdder(value1, value2, drawCircuit, simul)}")