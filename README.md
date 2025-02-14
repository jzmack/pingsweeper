# PingSweeper

A Python script that runs pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

## Installation

Script can be installed using `pip install pingsweeper`

### Requirements

- Python - https://www.python.org

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
python pip install pingsweeper==0.1.0
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the `README.md` file to better suit your project's needs. If you have any more questions or need further assistance, let me know!