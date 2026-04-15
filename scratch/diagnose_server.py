import socket

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"Connected to {host}:{port}")
            return True
    except Exception as e:
        print(f"Failed to connect to {host}:{port}: {e}")
        return False

import requests
def check_http(url):
    try:
        resp = requests.get(url, timeout=5)
        print(f"HTTP Status: {resp.status_code}")
        print(f"Response: {resp.text[:100]}")
    except Exception as e:
        print(f"HTTP Request failed: {e}")

if __name__ == "__main__":
    check_port("127.0.0.1", 8000)
    check_http("http://127.0.0.1:8000/")
    check_http("http://127.0.0.1:8000/deals")
