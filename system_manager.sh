#!/bin/bash
echo "===== FILE MANAGEMENT ====="

echo "--- Current Directory ---"
pwd

echo "--- Files ---"
ls -la

echo "--- Create Directory ---"
mkdir -p test_dir

echo "--- Create File ---"
touch test_dir/test.txt

echo "--- File Information ---"
ls -l test_dir/test.txt

echo "--- Disk Usage ---"
df -h

echo
echo "===== PROCESS MANAGEMENT ====="

echo "--- Running Processes ---"
ps aux

echo "--- Python Processes ---"
pgrep -a python3

echo "--- Memory ---"
free -h

echo "--- System Uptime ---"
uptime
