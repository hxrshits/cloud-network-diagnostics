import subprocess
import re
import socket
import sys
import json


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


def get_routing_table():
    result = subprocess.run(
        ["ip", "route"],
        capture_output=True,
        text=True,
        timeout=5
    )

    print("\nRouting Table")

    if result.returncode != 0:
        print("Error: Unable to retrieve routing table")
        return

    if result.stdout.strip():
        print(result.stdout.strip())
    else:
        print("No routes found")

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"Port {port:<5} : OPEN on {host}")

    except (socket.timeout, ConnectionRefusedError, OSError):
        print(f"Port {port:<5} : CLOSED or UNREACHABLE on {host}")


def check_network_health():
    print("\nNetwork Health Summary")

    checks = {}

    # Check 1: Default Gateway
    result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True,
        timeout=5
    )

    checks["Gateway"] = result.returncode == 0 and bool(result.stdout.strip())

    # Check 2: DNS Resolution
    try:
        socket.gethostbyname("google.com")
        checks["DNS"] = True
    except socket.gaierror:
        checks["DNS"] = False

    # Check 3: HTTPS Connectivity
    try:
        with socket.create_connection(("google.com", 443), timeout=3):
            checks["HTTPS"] = True
    except OSError:
        checks["HTTPS"] = False

    # Display results
    for name, status in checks.items():
        result = "PASS" if status else "FAIL"
        print(f"{name:<10}: {result}")

    # Overall status
    if all(checks.values()):
        print("\nOverall Network Status: HEALTHY")
    else:
        print("\nOverall Network Status: DEGRADED")


def run_diagnostics():
    print("\n" + "=" * 40)
    print("       NETWORK DIAGNOSTICS")
    print("=" * 40)

    checks = {}

    # Gateway check
    gateway_result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True,
        timeout=5
    )

    checks["Gateway"] = (
        gateway_result.returncode == 0
        and bool(gateway_result.stdout.strip())
    )

    # DNS check
    try:
        socket.gethostbyname("google.com")
        checks["DNS"] = True
    except socket.gaierror:
        checks["DNS"] = False

    # HTTPS check
    try:
        with socket.create_connection(
            ("google.com", 443), timeout=3
        ):
            checks["HTTPS"] = True
    except OSError:
        checks["HTTPS"] = False

    # Display diagnostic results
    for name, status in checks.items():
        print(f"{name:<12}: {'PASS' if status else 'FAIL'}")

    print("\nTroubleshooting Advice")

    if not checks["Gateway"]:
        print("- Check your default gateway and routing configuration.")

    if not checks["DNS"]:
        print("- Check DNS configuration and name resolution.")

    if not checks["HTTPS"]:
        print("- Check internet connectivity, firewall rules, and port 443 access.")

    if all(checks.values()):
        print("- All diagnostic checks passed.")

    print("=" * 40)



def generate_json_report():

    report = {
        "network_interface": None,
        "ipv4_address": None,
        "default_gateway": None,
        "dns_servers": [],
        "dns_resolution": "FAIL",
        "https_connectivity": "FAIL",
        "overall_status": "DEGRADED"
    }

    # Network interface and IPv4
    result = subprocess.run(
        ["ip", "-4", "-o", "addr", "show"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        for line in result.stdout.splitlines():
            parts = line.split()

            if len(parts) >= 4:
                report["network_interface"] = parts[1]
                report["ipv4_address"] = parts[3].split("/")[0]
                break

    # Default gateway
    result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        parts = result.stdout.split()

        if "via" in parts:
            report["default_gateway"] = parts[
                parts.index("via") + 1
            ]

    # DNS configuration
    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line.startswith("nameserver "):
                    report["dns_servers"].append(line.split()[1])

    except OSError:
        pass

    # DNS resolution
    try:
        socket.gethostbyname("google.com")
        report["dns_resolution"] = "PASS"
    except socket.gaierror:
        report["dns_resolution"] = "FAIL"

    # HTTPS connectivity
    try:
        with socket.create_connection(
            ("google.com", 443), timeout=3
        ):
            report["https_connectivity"] = "PASS"

    except OSError:
        report["https_connectivity"] = "FAIL"

    # Overall network status
    if (
        report["default_gateway"]
        and report["dns_resolution"] == "PASS"
        and report["https_connectivity"] == "PASS"
    ):
        report["overall_status"] = "HEALTHY"

    print(json.dumps(report, indent=4))

if __name__ == "__main__":

    if "--json" in sys.argv:
        generate_json_report()

    elif "--diagnose" in sys.argv:
        run_diagnostics()

    else:
        get_network_info()
        get_default_gateway()
        get_dns_config()
        check_dns()
        check_connectivity()
        get_routing_table()

        print("\nPort Connectivity Checks")
        check_port("google.com", 443)
        check_port("google.com", 80)

        check_network_health()
