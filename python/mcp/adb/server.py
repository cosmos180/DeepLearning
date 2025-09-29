"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-07-08 19:24:02
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-07-08 19:24:19
FilePath     : /DeepLearning/python/mcp/adb/server.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

# server.py
import json
import socket
import threading
import subprocess

HOST = "0.0.0.0"
PORT = 5000

# Supported commands mapping to adb shell commands
ADB_COMMANDS = {
    "cpu": ["adb", "shell", "top", "-n", "1"],
    "memory": ["adb", "shell", "dumpsys", "meminfo"],
    "disk": ["adb", "shell", "df"],
    "process_list": ["adb", "shell", "ps"],
}


class MCPHandler(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def run(self):
        with self.conn:
            data = self.conn.recv(4096).decode("utf-8")
            try:
                request = json.loads(data)
                cmd = request.get("command")
                if cmd not in ADB_COMMANDS:
                    response = {"status": "error", "message": f"Unknown command: {cmd}"}
                else:
                    result = subprocess.run(
                        ADB_COMMANDS[cmd],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        response = {"status": "ok", "output": result.stdout}
                    else:
                        response = {
                            "status": "error",
                            "message": result.stderr.strip() or "Command failed",
                        }
            except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
                response = {"status": "error", "message": str(e)}

            self.conn.sendall(json.dumps(response).encode("utf-8"))


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"MCP server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            handler = MCPHandler(conn, addr)
            handler.start()


if __name__ == "__main__":
    start_server()
