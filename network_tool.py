import subprocess


def get_network_interfaces():
    result = subprocess.run(
        ["ip", "addr"],
        capture_output=True,
        text=True
    )

    print(result.stdout)


if __name__ == "__main__":
    get_network_interfaces()
