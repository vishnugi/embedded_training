import subprocess

SCRIPT = "./system_manager.sh"

result = subprocess.run(
    [SCRIPT],
    capture_output=True,
    text=True
)

print("===== SHELL SCRIPT OUTPUT =====")
print(result.stdout)

if result.stderr:
    print("===== ERROR =====")
    print(result.stderr)

print("Return code:", result.returncode)
