#!/usr/bin/env python3

import asyncio
import sys
import os
import platform
import argparse
import time
import json
import csv
from ipaddress import ip_network, ip_address, AddressValueError
from datetime import datetime
import subprocess
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PingSweeper:
    def __init__(self, timeout: float = 0.2, count: int = 1, max_concurrent: int = 100):
        self.timeout = timeout
        self.count = count
        self.max_concurrent = max_concurrent
        self.os_type = platform.system()
        self.results = []
        
    async def ping_host(self, ip: str) -> Tuple[str, str, bool, Optional[float]]:
        """Ping a single host asynchronously"""
        command = self._build_ping_command(ip)
        process = None
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout * self.count + 2
            )

            if process.returncode == 0:
                response_time = self._parse_response_time(stdout.decode())
                if response_time is not None:
                    hostname = await self._resolve_hostname(ip)
                    status_msg = f"Ping... {ip} - {hostname} - Status: UP - Response time: {response_time}"
                    return ip, status_msg, True, response_time
            
            return ip, f"Ping... {ip} - Status: DOWN - No Response", False, None
            
        except asyncio.TimeoutError:
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=1.0)
                except:
                    try:
                        process.kill()
                        await process.wait()
                    except:
                        pass
            return ip, f"Ping... {ip} - Status: DOWN - Timeout", False, None
        except Exception as e:
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except:
                    pass
            logger.debug(f"Error pinging {ip}: {e}")
            return ip, f"Ping... {ip} - Status: DOWN - Error", False, None

    def _build_ping_command(self, ip: str) -> List[str]:
        """Build ping command based on OS"""
        if self.os_type == "Windows":
            return ["ping", "-n", str(self.count), "-w", str(int(self.timeout * 1000)), ip]
        else:
            return ["ping", "-c", str(self.count), "-W", str(self.timeout), ip]

    def _parse_response_time(self, output: str) -> Optional[str]:
        """Parse response time from ping output"""
        try:
            if self.os_type == "Windows":
                for line in output.split('\n'):
                    if "Average = " in line:
                        return line.split("Average = ")[-1].strip()
            else:
                for line in output.split('\n'):
                    if "rtt min/avg/max/mdev" in line or "round-trip" in line:
                        parts = line.split('=')[1].split('/') if '=' in line else []
                        return f"{parts[1].strip()}ms" if len(parts) > 1 else None
        except (IndexError, AttributeError):
            pass
        return None

    async def _resolve_hostname(self, ip: str) -> str:
        """Resolve hostname for IP address"""
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                "nslookup", ip, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=2.0)

            if process.returncode == 0:
                output = stdout.decode().splitlines()
                for line in output:
                    line_lower = line.lower()
                    if "name =" in line_lower or "name:" in line_lower:
                        return line.split("=")[-1].strip() if "=" in line else line.split()[-1].strip()
                return "No hostname"
            return "Resolution failed"
        except asyncio.TimeoutError:
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=0.5)
                except:
                    try:
                        process.kill()
                        await process.wait()
                    except:
                        pass
            return "Resolution timeout"
        except Exception:
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except:
                    pass
            return "No hostname"

    async def sweep_network(self, ip_list: List[str], show_progress: bool = True) -> dict:
        """Sweep network with progress tracking"""
        total_ips = len(ip_list)
        if total_ips == 0:
            return {"total": 0, "up": 0, "down": 0, "results": []}
        
        print(f"Pinging {total_ips} hosts with {self.max_concurrent} concurrent connections...")
        
        # Use semaphore to limit concurrent connections
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def ping_with_semaphore(ip):
            async with semaphore:
                return await self.ping_host(ip)
        
        # Create tasks
        tasks = [ping_with_semaphore(str(ip)) for ip in ip_list]
        
        # Execute with progress tracking
        results = []
        completed = 0
        
        try:
            for coro in asyncio.as_completed(tasks):
                ip_str, result, is_up, response_time = await coro
                results.append({
                    'ip': ip_str,
                    'message': result,
                    'status': 'UP' if is_up else 'DOWN',
                    'response_time': response_time,
                    'hostname': result.split(' - ')[1] if ' - ' in result and is_up else None
                })
                completed += 1
                
                if show_progress:
                    progress = completed / total_ips * 100
                    bar_length = 40
                    filled = int(progress * bar_length // 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f'\rProgress: [{bar}] {progress:.1f}% ({completed}/{total_ips})', end='')
        
            if show_progress:
                print()  # New line after progress bar
            
            # Sort results by IP
            results.sort(key=lambda x: ip_address(x['ip']))
            
            # Count statistics
            up_count = sum(1 for r in results if r['status'] == 'UP')
            down_count = total_ips - up_count
            
            # Display results
            print(f"\nScan Results:")
            print(f"IPs Scanned: {total_ips}")
            print(f"Hosts UP: {up_count}")
            print(f"Hosts DOWN: {down_count}")
            print(f"Success Rate: {(up_count/total_ips)*100:.1f}%")
            
            # Show live hosts summary
            if up_count > 0:
                print(f"\nLive Hosts ({up_count}):")
                for result in results:
                    if result['status'] == 'UP':
                        print(f"  {result['message']}")
            
            if up_count == 0:
                print("\nNo hosts responded to ping.")
            
            return {
                'total': total_ips,
                'up': up_count,
                'down': down_count,
                'success_rate': (up_count/total_ips)*100,
                'results': results
            }
        
        except Exception as e:
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except:
                pass
                
            raise e
def parse_ip_input(ip_input: str) -> List[str]:
    """Parse various IP input formats"""
    try:
        # Try CIDR notation first
        network = ip_network(ip_input, strict=False)
        return [str(ip) for ip in network.hosts()] if network.num_addresses > 2 else [str(network.network_address)]
    except ValueError:
        # Try single IP
        try:
            ip_address(ip_input)
            return [ip_input]
        except ValueError:
            # Try IP range (e.g., 192.168.1.1-192.168.1.50)
            if '-' in ip_input:
                start_ip, end_ip = ip_input.split('-', 1)
                start_ip = ip_address(start_ip.strip())
                end_ip = ip_address(end_ip.strip())
                if start_ip > end_ip:
                    raise ValueError("Start IP must be less than or equal to end IP")
                return [str(ip_address(ip)) for ip in range(int(start_ip), int(end_ip) + 1)]
            raise ValueError(f"Invalid IP format: {ip_input}")

def get_user_input(prompt: str) -> List[str]:
    """Get and validate user input for IP addresses"""
    try:
        while True:
            user_input = input(prompt).strip()
            if not user_input:
                print("Please enter a valid IP address, range, or subnet.")
                continue
            
            try:
                return parse_ip_input(user_input)
            except ValueError as e:
                print(f"Invalid input: {e}")
                print("Examples: 192.168.1.0/24, 10.0.0.1-10.0.0.50, 192.168.1.1")
                continue
    except KeyboardInterrupt:
        print("\nOperation interrupted. Exiting...")
        sys.exit(0)

def save_results(results_data: dict, output_format: str, filename_prefix: str = "sweep_results"):
    """Save results in specified format"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = "sweep_results"
    os.makedirs(results_dir, exist_ok=True)
    
    if output_format == "txt":
        filename = f"{results_dir}/{filename_prefix}_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(f"PING SWEEP RESULTS - {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total IPs Scanned: {results_data['total']}\n")
            f.write(f"Hosts UP: {results_data['up']}\n")
            f.write(f"Hosts DOWN: {results_data['down']}\n")
            f.write(f"Success Rate: {results_data['success_rate']:.1f}%\n\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 40 + "\n")
            for result in results_data['results']:
                f.write(f"{result['message']}\n")
    
    elif output_format == "csv":
        filename = f"{results_dir}/{filename_prefix}_{timestamp}.csv"
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["IP", "Status", "Hostname", "Response Time (ms)"])
            for result in results_data['results']:
                writer.writerow([
                    result['ip'], 
                    result['status'], 
                    result['hostname'] or 'N/A',
                    result['response_time'] or 'N/A'
                ])
    
    elif output_format == "json":
        filename = f"{results_dir}/{filename_prefix}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": results_data['total'],
                    "up": results_data['up'],
                    "down": results_data['down'],
                    "success_rate": results_data['success_rate']
                },
                "results": results_data['results']
            }, f, indent=2)
    
    print(f"Results saved to: {filename}")
    return filename

async def run_scan(sweeper, ip_list, show_progress):
    """Run the scan with proper cleanup"""
    try:
        results = await sweeper.sweep_network(ip_list, show_progress)
        # Small delay to allow subprocess cleanup
        await asyncio.sleep(0.1)
        return results
    except Exception as e:
        # Allow some time for cleanup before re-raising
        await asyncio.sleep(0.1)
        raise e

def main():
    parser = argparse.ArgumentParser(
        description="Fast asynchronous network ping sweeper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -s 192.168.1.0/24              # Scan subnet
  %(prog)s -s 10.0.0.1-10.0.0.50          # Scan IP range  
  %(prog)s -s 192.168.1.1                 # Scan single IP
  %(prog)s -s 192.168.1.0/24 --csv        # Save as CSV
  %(prog)s -s 192.168.1.0/24 -c 3 -t 1.0  # 3 pings, 1 second timeout
        """
    )
    
    parser.add_argument("-s", "--subnet", type=str, 
                       help="IP address, range (IP1-IP2), or subnet in CIDR notation")
    parser.add_argument("-t", "--timeout", type=float, default=0.2, 
                       help="Timeout per ping in seconds (default: 0.2)")
    parser.add_argument("-c", "--count", type=int, default=1, 
                       help="Number of ping packets per host (default: 1)")
    parser.add_argument("--max-concurrent", type=int, default=100, 
                       help="Maximum concurrent pings (default: 100)")
    parser.add_argument("--txt", action="store_true", 
                       help="Save results as text file")
    parser.add_argument("--csv", action="store_true", 
                       help="Save results as CSV file")
    parser.add_argument("--json", action="store_true", 
                       help="Save results as JSON file")
    parser.add_argument("--no-progress", action="store_true", 
                       help="Disable progress bar")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Coming soon... Only show summary, suppress individual results")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Coming soon... Enable verbose output for debugging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Get IP list
        if args.subnet:
            ip_list = parse_ip_input(args.subnet)
        else:
            ip_list = get_user_input("Enter IP address, range, or subnet: ")
        
        # Validate parameters
        if args.timeout <= 0:
            print("Error: Timeout must be positive")
            return 1
        
        if args.count <= 0:
            print("Error: Count must be positive")
            return 1
            
        if len(ip_list) > 65536:
            print(f"Warning: Scanning {len(ip_list)} hosts may take a while...")
            response = input("Continue? (y/N): ").lower()
            if response != 'y':
                return 0
        
        # Create sweeper and run scan
        sweeper = PingSweeper(args.timeout, args.count, args.max_concurrent)
        start_time = time.perf_counter()
        
        results = asyncio.run(run_scan(
            sweeper, 
            ip_list, 
            show_progress=not args.no_progress
        ))
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        print(f"\nScan completed in {execution_time:.2f} seconds")
        print(f"Average: {(execution_time/len(ip_list)*1000):.1f}ms per host")
        
        # Save results if requested
        if args.txt:
            save_results(results, "txt")
        if args.csv:
            save_results(results, "csv")
        if args.json:
            save_results(results, "json")
            
        return 0
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())