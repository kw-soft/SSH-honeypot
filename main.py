import json
import socket
import paramiko
import psycopg2
from threading import Thread, Event
import time
import signal
import sys
import select
from datetime import datetime

# -------------------------------------------------------------------
# 1) Load database configuration from config.json
# -------------------------------------------------------------------
def load_db_config(config_file="config.json"):
    """
    Loads the database configuration from a JSON file.
    Returns a dictionary containing host, port, database, user, and password.
    """
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"[-] Configuration file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[-] Error parsing '{config_file}'. Is it valid JSON?")
        sys.exit(1)

db_config = load_db_config()

# -------------------------------------------------------------------
# 2) Functions to store data in PostgreSQL
# -------------------------------------------------------------------

def store_login_attempt(ip, port, username, password):
    """
    Stores a full login attempt in the 'login_attempts' table,
    including IP, port, username, and password.
    """
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO login_attempts (ip, port, username, password)
            VALUES (%s, %s, %s, %s)
            """,
            (ip, port, username, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] Error storing full attempt in DB: {e}")


def store_credentials_only(username, password):
    """
    Stores only username and password in the 'harvested_credentials' table,
    along with a timestamp (created_at).
    """
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO harvested_credentials (username, password, created_at)
            VALUES (%s, %s, %s)
            """,
            (username, password, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] Error storing credentials in DB: {e}")


def store_ip_access(ip):
    """
    Stores only the IP address in the 'ip_access' table,
    along with a timestamp (accessed_at).
    """
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ip_access (ip, accessed_at)
            VALUES (%s, %s)
            """,
            (ip, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] Error storing IP access in DB: {e}")

# -------------------------------------------------------------------
# 3) SSH Tarpit Logic
# -------------------------------------------------------------------

# Generate a fake host key for the SSH server
HOST_KEY = paramiko.RSAKey.generate(2048)

# Control event to signal the server to stop
stop_event = Event()

# List to track active threads and sockets
active_connections = []

# Fake SSH server for the tarpit
class PersistentTarpitSSHServer(paramiko.ServerInterface):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = 22

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # Log the attempt
        print(f"[!] Login attempt: {username}:{password}")

        # 1) Store the full attempt in 'login_attempts'
        store_login_attempt(self.ip, self.port, username, password)

        # 2) Store only credentials (username & password) in 'harvested_credentials'
        store_credentials_only(username, password)

        # Artificial delay (tarpit effect)
        time.sleep(2)

        # Always reject authentication
        return paramiko.AUTH_FAILED

# Function to handle individual connections
def handle_persistent_tarpit(client_socket, client_address):
    print(f"[+] Connection from {client_address}")
    transport = None
    active_connections.append(client_socket)  # Track the socket

    # 3) Store IP access (we log the IP address as soon as a new connection arrives)
    store_ip_access(client_address[0])

    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)

        # Create the server object with IP/Port
        server = PersistentTarpitSSHServer(client_address[0], client_address[1])
        transport.start_server(server=server)

        # Keep connection alive while transport is active and server isn't stopped
        while transport.is_active() and not stop_event.is_set():
            try:
                time.sleep(10)  # Additional delay
            except Exception as e:
                print(f"[-] Error with {client_address}: {e}")
                break

    except paramiko.SSHException as ssh_err:
        print(f"[-] SSH error with {client_address}: {ssh_err}")
    except Exception as e:
        print(f"[-] General error with {client_address}: {e}")
    finally:
        if transport:
            transport.close()  # Close transport cleanly
        client_socket.close()  # Close client socket cleanly
        active_connections.remove(client_socket)  # Remove from active connections
        print(f"[-] Connection to {client_address} closed")

# Function to stop the server
def stop_server(signal_received, frame):
    print("\n[!] Stopping server...")
    stop_event.set()  # Signal all threads to stop
    # Close all active connections
    for conn in active_connections:
        conn.close()
    sys.exit(0)  # Exit the program cleanly

# Main function to start the tarpit
def start_persistent_tarpit(host='0.0.0.0', port=2222):
    print(f"[+] SSH Tarpit running on {host}:{port}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(100)  # Queue up to 100 connections
    server_socket.setblocking(False)  # Make the socket non-blocking

    # Register signal handler
    signal.signal(signal.SIGINT, stop_server)

    try:
        while not stop_event.is_set():
            # Use select to handle non-blocking socket accept
            readable, _, _ = select.select([server_socket], [], [], 1)
            for s in readable:
                client_socket, client_address = s.accept()
                print(f"[+] New connection from {client_address}")
                client_thread = Thread(
                    target=handle_persistent_tarpit,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True  # Ensure threads exit properly
                client_thread.start()
    except Exception as e:
        if not stop_event.is_set():
            print(f"[-] Error in server loop: {e}")
    finally:
        server_socket.close()
        print("[+] Server has been stopped.")

if __name__ == "__main__":
    start_persistent_tarpit()
