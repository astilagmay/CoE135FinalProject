# AstiDrop

A portable cross-platform program that replicates Apple's AirDrop written in Python. Explores the advantages, disadvantages, and the application of multithreading/multiprocessing in computer programs.

## Files and Purpose

Main Programs:
* main.py - the main program, uses one socket per subprocess
* main_serial.py - a variant of the main program that uses only one socket

Benchmarks for Multiprocessed Program (Multiple and Single Files)
* multip_bench_multi.py
* multip_bench_single.py

Benchmarks for Serial Program (Multiple and Single Files)
* serial_bench_multi.py
* serial_bench_single.py

## Constraints

The program only works for devices on the same local network. The program was tested on Python 3.6.5 and Python 3.8. The program neglects Firewall, UDP Broadcast, and other constraints. The program also has a primitive directory menu and traversal thus it assumes that the files to be sent are in a specific folder in a specific directory.

## Usage

Put all files to be sent in a folder named "Files". This is required to be in the same directory as the repository folder "coe135project".

Simply run 
```
python3 main.py
```

## Benchmarks

Tested on the same network without other devices connected to it.

Format: send_time | receive_time

### Serial (Single Socket)

* 1 MB file:  0.29s | 0.28s

* 100 MB file:    21.80s | 20.78s

* 1GB file:   175.55s | 177.48s

* 30 files (8-12MB each): 67.28s | 66.853s

### Multiprocess (Multiple Sockets)

* 1 MB file:  0.24s | 0.28s

* 100 MB file:    49.38s | 50.47s

* 1GB file:   223.32s | 224.96s

* 30 files (8-12MB each): 1460.06s | 1489.32s


## Authors

* **Arnold Constantin B. Lagmay**

## Acknowledgments

Special thanks to:
* StackOverflow
* Python Documentation
* Beej's Guide To Network Programming
