# PingSweep

A Python script that runs pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

## Known Issues

This script was originally designed for Windows and its functionality on Linux/Mac systems is currently limited.

## Installation

This method of installation uses creates a virtual environment, installs required modules and packages, then clones the git repository. You'll need an SSH key in order to clone the repository. 

### Requirements

- Python - https://www.python.org
- Git - https://git-scm.com/
- GitHub ssh key - https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Setting up script for Windows
> Example here uses PowerShell. Python can be installed from the Microsoft store.

Installing Git for cloning of repository:
```sh
winget install --id Git.Git -e --source winget
```
> If `winget` is not installed, it can be installed from the Microsoft store.

Install 'virtualenv' module:
```sh
pip install virtualenv
```
Create folder to store virtual environments:
```sh
cd ~
mkdir .venvs
```
Create and activate virtual environment:
```sh
cd .venvs
python -m virtualenv pingsweep --prompt pingsweep
cd .\pingsweep\Scripts
.\activate
```
Clone git repository:
```sh
cd ~
mkdir python_projects #optionally you can create a folder to store project
cd python_projects
git clone git@github.com:jzmack/pingsweep.git
```
Install necesarry Python modules:
```sh
pip install -r requirements.txt
```

### Setting up script for Linux/Mac
> Example here is for a Debian based system.

Install required APT packages for virtual environment:
```sh
sudo apt update
sudo apt install python3-pip
sudo apt install python3-virtualenv
```
Create a folder to store virtual environments:
```sh
cd ~
mkdir .venvs
cd .venvs
```
Create virtual environment:
```sh
python3 -m virtualenv pingsweep --prompt pingsweep
source pingsweep/bin/activate
```
Install the required dependencies in virtual environment:
```sh
pip install -r requirements.txt
```
Clone the repository into the virtual environment:
```sh
git clone git@github.com:jzmack/pingsweep.git
cd pingsweep
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
```sh
python pingsweep.py -s 192.168.1.0/24 -t 0.5 -c 3
```
 - `-s` → Specifies the subnet in CIDR notation.
 - `-t` → Sets the timeout per ping (in seconds).
 - `-c` → Specifies the number of packets to send per host.
 
## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the `README.md` file to better suit your project's needs. If you have any more questions or need further assistance, let me know!