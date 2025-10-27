# PDC

This project implements sequential, parallel, and simulated distributed image processing.

## Tasks
sequential_process.py`: Processes images one by one
parallel_process.py`: Uses `multiprocessing.Pool` to process images in parallel
distributed_sim.py`: Simulates a 2-node distributed system
report.txt`: Contains the final analysis and results

## How to Run
1.  Install dependencies: `pip install Pillow`
2.  Run sequential test: `python sequential_process.py`
3.  Note the time, then edit `parallel_process.py` and `distributed_sim.py` with this time.
4.  Run parallel test: `python parallel_process.py`
5.  Run distributed test: `python distributed_sim.py`
