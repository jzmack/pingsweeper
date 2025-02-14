#modules needed
import concurrent.futures
import sys
import os
import subprocess
import argparse
from ipaddress import ip_network, AddressValueError
from datetime import datetime
#external modules
from pythonping import ping
from tqdm import tqdm

#to check if script has elevated permissions
def is_elevated():
    try:
        if os.name == "nt":  #Windows
            return True
        else:  #Linux/unix, macOS
            euid = os.geteuid()
            if euid != 0:  #not root
                print(f"Effective User ID(Unix-like): {euid}")
            return euid == 0
    except Exception as e:
        print(f"Error checking elevated permissions: {e}")
        return False

#function to run a ping
def pinger(ip, count, timeout):
    ip_str = str(ip)
    response = ping(ip_str, count=count, timeout=timeout)
    response_time = response.rtt_avg_ms
    if response.success and response.packet_loss == 0:
        hostname = nslookup(ip_str)
        return f"Ping... {ip_str} - {hostname} - Status: UP - Response time: {response_time} ms", True
    else:
        return f"Ping... {ip_str} - Status: DOWN - No Response", False

#function to run nslookup
def nslookup(ip_address):
    try:
        result = subprocess.run(["nslookup", ip_address], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.splitlines()
            for line in output:
                if "name =" in line.lower() or "name:" in line.lower():
                    return line.split("=")[-1].strip() if "=" in line else line.split()[-1].strip()
            for line in output:
                if "name" in line.lower():
                    return line.split(":")[-1].strip()
            return "Hostname not found"
        else:
            return f"nslookup failed: {result.stderr}"
    except Exception as e:
        return str(e)

#this function does a lot, sweeps subnet, generates output, and opens text file with results
def ping_sweeper(sweep_subnet, batch_size, timeout, count):
    total_up = 0
    all_results = []
    hosts_up = []
    total_ips = len(list(sweep_subnet))
    max_workers = min(64, (os.cpu_count() or 1) + 4)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor: #threading
        with tqdm(total=total_ips, desc="Pinging subnet...", position=0, leave=True) as progress_bar:
            for batch in batch_ips(sweep_subnet, batch_size):
                futures = {executor.submit(pinger, ip, count, timeout): ip for ip in batch}
                for future in sorted(concurrent.futures.as_completed(futures), key=lambda x: futures[x]):
                    result, is_up = future.result()
                    all_results.append(result)
                    if is_up:
                        hosts_up.append(result)
                        total_up += 1
                    progress_bar.update(1)

    hosts_pinged = f"IPs Pinged: {total_ips}"
    hosts_respond = f"Number of Responses: {total_up}"

    print(hosts_pinged)
    tqdm.write(hosts_respond) #print statement
    print("\n".join(hosts_up))

    all_results.append(hosts_pinged)
    all_results.append(hosts_respond)

    #creating a new directory and text file with results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("sweep_results"):
        os.makedirs("sweep_results")
    text_file = f"sweep_results/sweep_results_{timestamp}.txt"
    with open(text_file, "w") as f:
        f.write(hosts_pinged)
        f.write("\n" + hosts_respond + "\n" + "\n")
        for result in all_results:
            f.write(result + "\n")

    #checking OS to properly open file
    if os.name == "nt": #Windows
        subprocess.Popen(["notepad", f"sweep_results/sweep_results_{timestamp}.txt"])
    elif os.name =="posix":
        if sys.platform == "darwin": #macOS
            subprocess.Popen(["open", f"sweep_results/sweep_results_{timestamp}.txt"])
        else:
            subprocess.Popen(["xdg-open", f"sweep_results/sweep_results_{timestamp}.txt"]) #Linux/unix
    sys.exit()

#to batch the IP addresses
def batch_ips(sweep_subnet, batch_size):
    sweep_list = list(sweep_subnet)
    for i in range(0, len(sweep_list), batch_size):
        yield sweep_list[i:i + batch_size]

def get_user_input(prompt):
    try:
        while True:
            user_input = input(prompt)
            try: #validate input
                valid_input = ip_network(user_input)
                return valid_input
            except (ValueError, AddressValueError) as e:
                print(f"Invalid input: {e}")
                continue
    except KeyboardInterrupt:
        print("\nOperation interrupted. Exiting...")
        sys.exit(0)

#main function running the program
def main():
    parser = argparse.ArgumentParser(description="Python script for PingSweep.")
    parser.add_argument("-s", "--subnet", metavar="Subnet", type=str, help="Desired network to sweep in CIDR notation")
    parser.add_argument("-t", "--timeout", metavar="Timeout", type=float, default=0.25, help="Set a timeout in seconds. Default is 0.25 or 250ms")
    parser.add_argument("-c", "--count", metavar="Count", type=int, default=1, help="Amount of packets to send to each IP address. (will increase runtime)")
    args = parser.parse_args()

    try:
        sweep_subnet = ip_network(args.subnet) if args.subnet else get_user_input("Enter subnet in CIDR notation: ")
    except (ValueError, AddressValueError) as e:
        print(f"Invalid subnet{e}")
        return
    batch_size = 50
    try:
        ping_sweeper(sweep_subnet, timeout=args.timeout, count=args.count, batch_size=batch_size)
    except Exception as e:
        print(f"Error: {e}")

#running the program
if __name__ == "__main__":
    if is_elevated():
        main()
    else:
        print("Script requires elevated permissions to run.")
