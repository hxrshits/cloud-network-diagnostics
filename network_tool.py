import subprocess
import re


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


if __name__ == "__main__":
    get_network_info()
