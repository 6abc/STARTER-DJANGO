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
    
    devices = []
    dynamic_mac_count = 0
    vendor_mac_count = 0
    unknown_mac_count = 0

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        regex_pattern = r"^([\d\.]+)\s+([0-9a-f:]{17})\s+(.*)$"
        
        for line in output.splitlines():
            match = re.search(regex_pattern, line, re.IGNORECASE)
            if match:
                vendor_str = match.group(3).strip()
                v_lower = vendor_str.lower()
                
                # Logic to categorize MAC types
                if "locally administered" in v_lower:
                    dynamic_mac_count += 1
                elif "unknown" in v_lower:
                    unknown_mac_count += 1
                else:
                    # If it's not dynamic and not unknown, it's a recognized Vendor
                    vendor_mac_count += 1
                
                devices.append({
                    'ip': match.group(1),
                    'mac': match.group(2),
                    'vendor': vendor_str
                })
                
    except Exception as e:
        output = f"Error: {str(e)}"

    return render(request, 'app1/index.html', {
        'devices': devices,
        'dynamic_count': dynamic_mac_count,
        'vendor_count': vendor_mac_count,
        'unknown_count': unknown_mac_count, # Pass to template
        'interface': interface,
        'raw_output': output
    })