Benjamin A. Slack
CS5800
Assigment #3
DFA/NFA-Lambda Simulator

Description:
This project consists of two parts: simulator.py and the
python package, machine. Machine implements DFA (Deterministic
Finite Automaton) and NFA-Lambda (Nondeterministic Finite
Automaton) as well as convertion methods taking NFA-Lambda
into corresponding DFA. Simulator.py provides a command line
interface for performing these convertions and executions on
a given input string, known internally as a Tape.

Note! Implemented in Python 3.6.1 and uses the typing package
for parameter and return type hinting. Requires Python 3.6.1 or
higher. For instructions on how to install Python 3.6.1 for
your local environment see:

https://github.com/pyenv/pyenv

Usage:

<python3> simulator.py <tape> [--nfal filepath [--conv | --conv filepath]| --dfa filepath]

<python3> corresponds to your local binary of the python 3.6.1
interpreter. This maybe aliased on your system to python3 (Linux)
or it maybe an executable (e.g. python.exe on Windows)

<tape> refers to an input string that the machine the simulator
is creating will process. To enter an empty string, use "". Otherwise
the quote marks are not required to process your input.

--nfal filepath, instructs the simulator to produce a NFA-Lamba
using the corresponding configuration file.  Configuration files
take the form of JSON text files and contain the various required
sets to define a machine.

--conv [filepath], only to be used in tandem with --nfal, instructs
the simulator to convert the NFA-lambda to a DFA and perform an
execution on the given input string, returning the result to STDOUT.
Note! This is the only way an NFA-Lambda can perform an execution.
The filepath parameter is optional, and if not supplied, the
simulator will generate a DFA configuration file, of the same prefix
name and location as the NFA.

--dfa filepath, instructs the simulator to produce a DFA using the
supplied configuration file. Performs an execution of that machine
and returns the result to STDOUT.
