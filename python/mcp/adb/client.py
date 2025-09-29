"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-07-08 19:23:29
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-07-08 19:23:46
FilePath     : /DeepLearning/python/mcp/adb/client.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

# client.py
import json
import socket

HOST = "127.0.0.1"  # server address
PORT = 5000  # server port


def send_command(command):
    request = {"command": command}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(request).encode("utf-8"))
        data = s.recv(65536).decode("utf-8")
        response = json.loads(data)
        return response


if __name__ == "__main__":
    # 示例调用
    for cmd in ["cpu", "memory", "disk", "process_list", "invalid"]:
        print(f"--- {cmd} ---")
        resp = send_command(cmd)
        if resp["status"] == "ok":
            print(resp["output"])
        else:
            print(f"Error: {resp['message']}")
