import subprocess
import re
import socket

def get_network_info():
    result = subprocess.run(
        ["ip", "-4", "addr"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    current_interface = None

    for line in lines:
        interface_match = re.match(r"\d+:\s+([^:]+):", line)

        if interface_match:
            current_interface = interface_match.group(1)

        ip_match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", line)

        if ip_match and current_interface:
            ip_address = ip_match.group(1)

            print(f"Interface : {current_interface}")
            print(f"IPv4      : {ip_address}")
            print()


def get_default_gateway():
    result = subprocess.run(
        ["ip", "route"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():
        if line.startswith("default"):
            parts = line.split()

            if "via" in parts:
                gateway = parts[parts.index("via") + 1]
                interface = parts[parts.index("dev") + 1]

                print(f"Default Gateway : {gateway}")
                print(f"Gateway Interface: {interface}")
                return


def check_dns(domain="google.com"):
    try:
        ip_address = socket.gethostbyname(domain)

        print(f"DNS Check       : {domain}")
        print(f"Resolved IP     : {ip_address}")

    except socket.gaierror:
        print(f"DNS Check       : Failed to resolve {domain}")


    print("Default Gateway : Not found")


def check_connectivity(host="8.8.8.8"):
    result = subprocess.run(
        ["ping", "-c", "4", host],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"Connectivity    : {host} reachable")

        for line in result.stdout.splitlines():
            if "packet loss" in line:
                print(f"Packet Loss     : {line.strip()}")

            if "min/avg/max" in line:
                print(f"Latency         : {line.strip()}")
    else:
        print(f"Connectivity    : {host} unreachable")



def get_dns_config():
    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as file:
            lines = file.readlines()

        servers = []

        for line in lines:
            line = line.strip()

            if line.startswith("nameserver "):
                server = line.split()[1]
                servers.append(server)

        print("\nDNS Configuration")

        if servers:
            for server in servers:
                print(f"DNS Server      : {server}")
        else:
            print("DNS Server      : No nameserver found")

    except OSError as error:
        print(f"DNS Configuration Error: {error}")



if __name__ == "__main__":
    get_network_info()
    get_default_gateway()
    get_dns_config()
    check_dns()
    check_connectivity()
