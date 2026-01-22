from django.shortcuts import render
import subprocess
import re

def get_default_interface():
    """Detects the primary network interface name."""
    try:
        # Run 'ip route' to find the default gateway line
        result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "default" in line:
                # The interface name usually follows the word 'dev'
                match = re.search(r"dev\s+(\S+)", line)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return "eth0"  # Fallback to your known working interface

def index(request):
    interface = get_default_interface()
    command = ["/usr/sbin/arp-scan", "-I", interface, "--localnet"]
    devices = [] # This will hold our list of dictionaries

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        
        # Regex explanation:
        # ([\d\.]+)       -> Group 1: Matches the IP (digits and dots)
        # \s+             -> Matches the whitespace/tab
        # ([0-9a-f:]{17}) -> Group 2: Matches the MAC address (hex and colons)
        # \s+             -> Matches the whitespace/tab
        # (.*)            -> Group 3: Matches everything else (Vendor name)
        regex_pattern = r"^([\d\.]+)\s+([0-9a-f:]{17})\s+(.*)$"
        
        for line in output.splitlines():
            match = re.search(regex_pattern, line, re.IGNORECASE)
            if match:
                devices.append({
                    'ip': match.group(1),
                    'mac': match.group(2),
                    'vendor': match.group(3)
                })
                
    except Exception as e:
        output = f"Error: {str(e)}"

    return render(request, 'app1/index.html', {
        'devices': devices,
        'interface': interface,
        'raw_output': output # Kept just in case you want to debug
    })