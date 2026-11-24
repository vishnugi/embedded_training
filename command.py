import subprocess

# File management commands
commands = [
    "pwd",
    "ls -la",
    "mkdir -p test_dir",
    "touch test_dir/file.txt",
    "cp test_dir/file.txt test_dir/file2.txt",
    "mv test_dir/file2.txt test_dir/file3.txt",
    "ls -l test_dir",

    # Process management commands
    "ps aux",
    "ps -ef",
    "pgrep -a python",
    "pstree -p",
    "free -h",
    "uptime"
]

for cmd in commands:
    print(f"\n$ {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("ERROR:", result.stderr)
