import subprocess

result = subprocess.run(
    ["ip", "addr"],
    capture_output=True,
    text=True
)

print(result.stdout)

