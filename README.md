# PingSweeper

A Python script that runs pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

![Demo](docs/install_demo.gif)

## Installation

Script can be installed using `pip install pingsweeper`

### On Linux

Install in a virtual environment:
```sh
sudo apt update
sudo apt install python3-venv python3-pip
python3 -m venv .psvenv
source .psvenv/bin/activate
pip install pingsweeper
```

### Requirements

- Python - https://www.python.org
> Note: On Windows, the script will need to be in the PATH environment variable to work as demonstrated here.

## Usage

Running the script:
```sh
pingsweeper
```
To show available arguments:
```sh
pingsweeper -h
```
Example with all available arguments:
```sh
pingsweeper -s 192.168.1.0/24 -t 0.5 -c 3
```
 - `-s` → Specifies the subnet in CIDR notation.
 - `-t` → Sets the timeout per ping (in seconds).
 - `-c` → Specifies the number of packets to send per host.

Once the script completes, the console will print a summary including the number of hosts ping, hosts that responded, and the results of all the hosts that were UP. A text file with the results will be generated at `sweep_results/` and opened (assuming the system has a GUI).

## Upgrading

To upgrade to the latest version:
```shell
python -m pip install --upgrade pingsweeper
```
To install a specific version:
```shell
python pip install pingsweeper==0.1.1
```
## Possible issues

There have been cases where the following warning may be shown after installing the package which will not allow you to run `pingsweeper` as intended. If this is the case, then the file path highlighted will need added to the system PATH environment variable.

![Image](https://github.com/user-attachments/assets/c26eb4fd-1f63-47ac-9fb0-cad1d00fccc9)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
