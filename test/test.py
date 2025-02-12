import subprocess


def nslookup(ip_address):
    try:
        # Run the nslookup command
        lookup_result = subprocess.run(['nslookup', ip_address], capture_output=True, text=True)

        # Check if the command was successful
        if lookup_result.returncode == 0:
            return lookup_result.stdout  # Return the output of the command
        else:
            return f"nslookup failed: {lookup_result.stderr}"  # Return the error if the command failed
    except Exception as e:
        return str(e)  # Handle exceptions


# Example usage
ip = '10.103.6.241'
output = nslookup(ip)
print(output)
