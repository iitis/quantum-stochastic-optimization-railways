# quantum-stochastic-optimization-railways
application of quantum computation for stochastic optimization on example of railway/tramway network in Baltimore 

Files:

1. ```QTrains``` - source code
2. ```tests``` - testing source code
3. ```solutions``` - stored solutions of railway problems
4. ```QUBOs``` - qubos of railway problems
5. ```histograms``` - histograms from data analysis
6. ```histograms_soft``` - histograms from data analysis with soften check of minimal passing time constraint. Input QUBO is the same
as in the original problem, but for output minimal passing time constraint is not checked

The main script for computing on ILP and QUBO far various scenarios in ```solve_qubo.py```

Script ```qubo4gates.py``` saves qubo and ground state as well as analyses output dedicted to gates computiond
