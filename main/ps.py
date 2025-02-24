# modules needed
import concurrent.futures
import sys
import os
import subprocess
import platform
import argparse
from ipaddress import ip_network, ip_address, AddressValueError
from datetime import datetime
# external modules
from tqdm import tqdm

# checking OS
def get_os_type():
    return platform.system()

# function to run a ping
def pinger(ip, count, timeout):
    ip_str = str(ip_address(ip))
    os_type = get_os_type()
    command = ["ping", "-c" if os_type != "Windows" else "-n", str(count), "-W" if os_type != "Windows" else "-w", str(timeout if os_type != "Windows" else timeout * 1000), ip_str]

    try:
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if response.returncode == 0:
            response_time = parse_response_time(response.stdout, os_type)
            if response_time:
                hostname = nslookup(ip_str)
                return f"Ping... {ip_str} - {hostname} - Status: UP - Response time: {response_time}", True
            else:
                return f"Ping... {ip_str} - Status: DOWN - No Response", False
        else:
            return f"Ping... {ip_str} - Status: DOWN - No Response", False
    except Exception as e:
        return f"Ping... {ip_str} - Status: DOWN - Error: {str(e)}", False

# function to parse response time
def parse_response_time(output, os_type):
    if os_type == "Windows":
        for line in output.split('\n'):
            if "Average = " in line:
                return line.split("Average = ")[-1].strip()
    else:
        for line in output.split('\n'):
            if "rtt min/avg/max/mdev" in line:
                return line.split('=')[1].split('/')[1].strip()
    return None

# function to run nslookup
def nslookup(ip):
    try:
        result = subprocess.run(["nslookup", ip], capture_output=True, text=True)
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

# function to sweep subnet, generate output, and open text file with results
def ping_sweeper(ip_list, batch_size, timeout, count):
    total_up = 0
    all_results = []
    hosts_up = []
    total_ips = len(ip_list)
    max_workers = min(128, (os.cpu_count() or 1) * 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:  # threading
        with tqdm(total=total_ips, desc="Pinging subnet...", position=0, leave=True) as progress_bar:
            for batch in batch_ips(ip_list, batch_size):
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
    print(hosts_respond)
    print("\n".join(hosts_up))

    save_results(all_results, hosts_pinged, hosts_respond)
    return hosts_pinged, hosts_respond

# function to save results to a text file and open it
def save_results(all_results, hosts_pinged, host_respond):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    clean_timestamp = datetime.now().strftime("%m/%d/%Y - %H:%M")
    if not os.path.exists("sweep_results"):
        os.makedirs("sweep_results")
    text_file = f"sweep_results/sweep_results_{timestamp}.txt"

    with open(text_file, "w") as f:
        f.write(f"TIMESTAMP: {clean_timestamp}\n\n")
        f.write(f"{hosts_pinged}")
        f.write(f"\n{host_respond}\n\n")
        f.write("\n".join(all_results))

    open_results_file(text_file)

# function to open results file based on OS
def open_results_file(file_path):
    try:
        if os.name == "nt":  # Windows
            subprocess.Popen(["notepad", file_path])
        elif os.name == "posix":
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])  # Linux/unix
    except Exception as e:
        print(f"Could not open text file. {e}")
        print("Results are saved at sweep_results/")

# to batch the IP addresses
def batch_ips(ip_list, batch_size):
    for i in range(0, len(ip_list), batch_size):
        yield ip_list[i:i + batch_size]

# function to get network from user
def get_user_input(prompt):
    try:
        while True:
            user_input = input(prompt)
            try:  # validate input
                valid_input = ip_network(user_input)
                return valid_input
            except (ValueError, AddressValueError) as e:
                print(f"Invalid input: {e}")
                continue
    except KeyboardInterrupt:
        print("\nOperation interrupted. Exiting...")
        sys.exit(0)

# function to get IP range from user
def get_ip_range():
    try:
        while True:
            start_ip = input("Starting IP: ")
            end_ip = input("Ending IP: ")
            try:
                start_ip = ip_address(start_ip)
                end_ip = ip_address(end_ip)
                if start_ip > end_ip:
                    print("Starting IP must be less than or equal to Ending IP.")
                    continue
                return [ip_address(ip) for ip in range(int(start_ip), int(end_ip) + 1)]
            except ValueError as e:
                print(f"Invalid IP address: {e}")
                continue
    except KeyboardInterrupt:
        print("\nOperation interrupted. Exiting...")
        sys.exit(0)

# main function running the program
def main():
    parser = argparse.ArgumentParser(description="Python script for PingSweeper.")
    parser.add_argument("-s", "--subnet", metavar="Subnet", type=str, help="Desired network to sweep in CIDR notation")
    parser.add_argument("-r", "--range", action="store_true", help="Use IP range instead of subnet")
    parser.add_argument("-t", "--timeout", metavar="Timeout", type=float, default=0.2, help="Set a timeout in seconds. Default is 0.20 or 200ms")
    parser.add_argument("-c", "--count", metavar="Count", type=int, default=1, help="Amount of packets to send to each IP address. (will increase runtime)")
    args = parser.parse_args()

    try:
        if args.range:
            ip_list = get_ip_range()
        else:
            sweep_subnet = ip_network(args.subnet) if args.subnet else get_user_input("Enter subnet in CIDR notation: ")
            ip_list = list(sweep_subnet.hosts())
    except (ValueError, AddressValueError) as e:
        print(f"Invalid input {e}")
        return
    batch_size = 100
    try:
        ping_sweeper(ip_list, timeout=args.timeout, count=args.count, batch_size=batch_size)
    except Exception as e:
        print(f"Error: {e}")

# running the program
if __name__ == "__main__":
    main()