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

Once the script completes, the console will print a summary including the number of hosts ping, hosts that responded, and the results of all the hosts that were UP. Also, a text file will be created at `sweep_results/`. If running on Windows, the text file will open.  

### Working with Linux/Macs
> Note: A virtual environment (venv) is recommended to run this script on Unix-based systems.

Due to the nature of this script sending out raw ICMP packets, elevated permissions are required to run. This workaround creates a virtual environment for the package to live in. Then, we'll create wrapper script and add it to the PATH to enable the same functionality as when ran on Windows systems.

Prepping virtual environment:
```shell
cd ~
mkdir ~/.venvs #creating a hidden folder for venvs
mkdir ~/.venvs/psvenv #creating a folder for our pingsweeper environment
python3 -m venv ~/.venvs/psvenv #creating a virtual environment in our new folder
source ~/.venvs/psvenv/bin/activate #activating the venv
pip install pingsweeper #installing package in the venv
```
Create a file for the wrapper script:
```shell
nano ~/pingsweeper_wrapper
```
Add the file path of your venv's instance of Python, and the path file. Change "your_username" to the name of the local user. Once filled in press Ctrl + O then Enter to save. Then Ctrl+X to go back to the console.
```nano
#!/bin/bash
sudo /home/your_username/.venvs/bin/python3 /home/your_username/.venvs/bin/pingsweeper  #change username on this line
```
Make the `pingsweeper_wrapper` file executable, then add it to a directory in your PATH.
```shell
chmod +x ~/pingsweeper_wrapper
sudo mv ~/pingsweeper_wrapper /usr/local/bin/pingsweeper
```
Verify that the script now works as intended
```shell
pingsweeper
```
## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the `README.md` file to better suit your project's needs. If you have any more questions or need further assistance, let me know!