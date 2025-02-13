# PingSweep

A Python script that runs pings to determine how many hosts are up on a specified subnet. This script will also run a DNS lookup to find host names if they are available.

## Known Issues

This script was originally designed for Windows and its functionality on Linux/Mac systems is currently limited.

## Installation

This method of installation creates a virtual environment, installs required modules and packages, then clones the git repository. You'll need an SSH key in order to clone the repository.

### Requirements

- Python - https://www.python.org
- Git - https://git-scm.com/
- GitHub ssh key - https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Setting up script for Windows
> Example here uses PowerShell. Python can be installed from the Microsoft store.

Installing Git for cloning the repository:
```sh
winget install --id Git.Git -e --source winget
```
> If `winget` is not installed, it can be installed from the Microsoft store.
> If you've never pulled from GitHub, you'll need to create a GitHub account, generate an SSH key, and add the Key to your account's SSH key store.

#### Git setup after GitHub account is created:
Generate a new SSH key. Enter a passphrase and press enter to store it in the default location which is usually C:\Users\user_name\.ssh
```sh
ssh-keygen.exe -t ed25519 -C "your_email@example.com" # replace with your email
```
Start the ssh-agent service and add the SSH key to the ssh-agent. You'll need to enter the passphrase. 
```sh
Start-Process powershell -Argument"-Command", "Start-Service ssh-agent" -Verb runAs # opens admin PowerShell to start the ssh-agent service
ssh-add C:\Users\user_name\.ssh\id_ed25519 # replace with actual path
```
Show the contents of the `id_ed25519.pub` file. Copy the entire output and paste into your GitHub SSH key store at Settings > SSH and GPG Keys > New SSH Key
```sh
Get-Content C:\Users\user_name\.ssh\id_ed25519.pub # replace with actual path
```
#### Installing the virtual environment and requirements
Here is a recommended way to create/store your virtual environment.
```sh
pip install virtualenv # install 'virtualenv' module
cd ~
mkdir .venvs # create folder to store virtual environments:
cd .venvs
python -m virtualenv psvenv --prompt psvenv # create virtual environment --prompt is optional
cd .\pingsweep\Scripts
.\activate # activate newly created virtual environment
```
Clone git repository:
```sh
cd ~
mkdir python_projects #optionally you can create a folder to store project
cd python_projects
git clone git@github.com:jzmack/pingsweep.git
```
Install the necesarry Python modules:
```sh
pip install -r requirements.txt
```
Python files are located in the `main` folder

### Setting up script for Linux/Mac
> Example here is for a Debian based system.

Install required APT packages for the virtual environment:
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
Clone the repository into the virtual environment:
```sh
git clone git@github.com:jzmack/pingsweep.git
cd pingsweep
```
Install the required dependencies in virtual environment:
```sh
pip install -r requirements.txt
```
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