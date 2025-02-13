# PingSweeper

A Python script that runs pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

## Known Issues

This script was originally designed for Windows and its functionality on Linux/Mac systems is currently limited.

## Installation

Script can be installed using `pip install pingsweeper`

### Requirements

- Python - https://www.python.org

## Usage

Running the script:
```sh
python pingsweep.py
```
To show available arguments:
```sh
python pingsweep.py -h
```
Example with all available arguments:
```sh
python pingsweep.py -s 192.168.1.0/24 -t 0.5 -c 3
```
 - `-s` → Specifies the subnet in CIDR notation.
 - `-t` → Sets the timeout per ping (in seconds).
 - `-c` → Specifies the number of packets to send per host.
 
## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the `README.md` file to better suit your project's needs. If you have any more questions or need further assistance, let me know!