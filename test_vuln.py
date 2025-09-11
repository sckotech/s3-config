import os
import subprocess

# Hardcoded secret (should trigger)
API_KEY = "12345-SECRET-HARDCODED"

# Command injection (should trigger)
user_input = input("Enter command: ")
subprocess.call("ls " + user_input, shell=True)

# SQL injection (should trigger)
import sqlite3
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
user = input("Enter username: ")
cursor.execute("SELECT * FROM users WHERE name = '" + user + "';")
