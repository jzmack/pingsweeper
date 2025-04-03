#!/usr/bin/env python3

import asyncio
import sys
import os
import platform
import argparse
import time
from ipaddress import ip_network, ip_address, AddressValueError
from datetime import datetime
import subprocess

# checking OS
def get_os_type():
    return platform.system()

# function to run a ping asynchronously
async def pinger(ip, count, timeout):
    ip_str = str(ip_address(ip))
    os_type = get_os_type()
    command = ["ping", "-c" if os_type != "Windows" else "-n", str(count), "-W" if os_type != "Windows" else "-w", str(timeout if os_type != "Windows" else timeout * 1000), ip_str]

    try:
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            response_time = parse_response_time(stdout.decode(), os_type)
            if response_time:
                hostname = await nslookup(ip_str)
                return ip_str, f"Ping... {ip_str} - {hostname} - Status: UP - Response time: {response_time}", True
            else:
                return ip_str, f"Ping... {ip_str} - Status: DOWN - No Response", False
        else:
            return ip_str, f"Ping... {ip_str} - Status: DOWN - No Response", False
    except Exception as e:
        return ip_str, f"Ping... {ip_str} - Status: DOWN - Error: {str(e)}", False

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

# function to run nslookup asynchronously
async def nslookup(ip):
    try:
        process = await asyncio.create_subprocess_exec("nslookup", ip, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode().splitlines()
            for line in output:
                if "name =" in line.lower() or "name:" in line.lower():
                    return line.split("=")[-1].strip() if "=" in line else line.split()[-1].strip()
            for line in output:
                if "name" in line.lower():
                    return line.split(":")[-1].strip()
            return "Hostname not found"
        else:
            return f"nslookup failed: {stderr.decode()}"
    except Exception as e:
        return str(e)

# function to sweep subnet, generate output, and open text file with results
async def ping_sweeper(ip_list, batch_size, timeout, count):
    total_up = 0
    all_results = []
    hosts_up = []
    total_ips = len(ip_list)

    print("Pinging subnet...")
    tasks = {ip: pinger(ip, count, timeout) for ip in ip_list}
    for i, coro in enumerate(asyncio.as_completed(tasks.values())):
        ip_str, result, is_up = await coro
        all_results.append((ip_str, result))
        if is_up:
            hosts_up.append(result)
            total_up += 1
        # Update custom progress bar
        progress = (i + 1) / total_ips * 100
        print(f"\rProgress: [{'#' * int(progress // 5)}{'.' * (20 - int(progress // 5))}] {progress:.2f}%", end='')

    all_results.sort(key=lambda x: ip_address(x[0]))
    ordered_results = [result for _, result in all_results]

    hosts_pinged = f"\nIPs Pinged: {total_ips}"
    hosts_respond = f"Number of Responses: {total_up}"

    print("\n" + hosts_pinged)
    print(hosts_respond)
    print("\n".join(ordered_results))

    save_results(ordered_results, hosts_pinged, hosts_respond)
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
        asyncio.run(ping_sweeper(ip_list, timeout=args.timeout, count=args.count, batch_size=batch_size))
    except Exception as e:
        print(f"Error: {e}")

# running the program
if __name__ == "__main__":
    main()