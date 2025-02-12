# PingSweep

PingSweep is a Python script that runs a pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

## Installation

1. Clone the repository:
```sh
git clone git@github.com:jzmack/pingsweep.git
cd pingsweep
```
2. Install the required dependencies:
```sh
pip install -r requirements.txt
```
## Usage

Running the script:
```sh
python pingsweep.py
```
Run to show available arguments:
```sh
python pingsweep.py -h
```
Run the script with the desired subnet in CIDR notation:
```sh
python pingsweep.py -s 192.168.1.0/24
```
You can also specify the timeout and the number (count) of packets to send:
```sh
python pingsweep.py -s 192.168.1.0/24 -t 0.5 -c 3
```
## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the `README.md` file to better suit your project's needs. If you have any more questions or need further assistance, let me know!

