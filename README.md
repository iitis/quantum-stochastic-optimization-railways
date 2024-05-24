# quantum-stochastic-optimization-railways
Application of quantum computation for stochastic optimization on example of railway/tramway network in Baltimore.

Files:

1. ```QTrains``` - source code
2. ```tests``` - testing source code

3. ```solutions``` - stored solutions of railway problems, if for particular parameters setting computations has already been stored, new computation will not be performed and the particluar file will not be overwritten
4. ```QUBOs``` - qubos of railway problems
5. ```QAOA Results``` - results of quantum gate computing via QAOA
6. ```histograms``` - histograms from data analysis
7. ```histograms_soft``` - histograms from data analysis with soften check of minimal passing time constrain.


#### Quantum annealing 

In ```process_q_annealing.py ``` trains scheduling problems are solved via Integer Linear Programming and quantum (or simulated) annealing

Arguments:

- --mode MODE: process mode: 0: prepare only QUBO, 1: make, computation (ILP and annealing), 2: analyze outputs, 3: count q-bits, 4: prepare Ising model - by dafault: ```2```
- --simulation SIMULATION: if True solve / analyze output of simulated annealing (via DWave software), if False real annealing - by default: False
- --softern_pass SOFTERN_PASS: if true analyze output without feasibility check on minimal passing time constrain - by default: False


Example usage:

```python3 process_q_annealing.py --mode 1 --sim True```

Solve the series of problems by simulated annealing (does not perform calculations already performed and saved).

```python3 process_q_annealing.py --mode 1```

Solve the series of problems by real D-Wave annealing (does not perform calculations already performed and saved).

```python3 process_q_annealing.py --mode 2 --softern_pass True```



#### Quantum gate computing

Script ```process_q_gates.py``` saves QUBO and ground state as well as analyses output dedicated to gates computing.

Arguments:

- --notrains NOTRAINS  number of trains, 1,2,4 are supported, by default: ``2``
- --savequbo SAVEQUBO  if True prepare qubo else analyze outputs, by default: False
- --nolayers NOLAYERS  number of layers of QAOA in analyzed data, by default: ```1```
- --datafile DATAFILE  file with data, by default:  ```"QAOA Results/IonQ Simulations/"```


Example usage:

```python3 process_q_gates.py --notrains 2 --nolayer 1 --datafile "QAOA Results/IonQ Simulations/" ```

Analyzes ```2``` trains results in ```"QAOA Results/IonQ Simulations/" ``` where ```2``` layers of QAOA was used

```python3 process_q_gates.py --notrains 2 --savequbo true ```

Prepared QUBOs for ```2``` trains problems and save them in ```QUBOs/gates/2trains/```

#### Preparing plots for article

Script ```plots4article.py``` creates csv files for high quality plots for the purpose of article, and save them in ```article_plots``` folder.


# Funding

Scientific work co-financed from the state budget under the program of the Minister of Education and Science, Poland (pl. Polska) under the name "Science for Society II" project number NdS-II/SP/0336/2024/01 funding amount ... total value of the project ```1000000``` PLN 
