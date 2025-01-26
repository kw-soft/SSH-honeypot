import socket
import paramiko
from threading import Thread, Event
import time
import signal
import sys
import select

# Generate a fake host key for the SSH server
HOST_KEY = paramiko.RSAKey.generate(2048)

# Control event to signal the server to stop
stop_event = Event()

# List to track active threads and sockets
active_connections = []

# Fake SSH server for the tarpit
class PersistentTarpitSSHServer(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(f"[!] Login attempt: {username}:{password}")
        time.sleep(2)  # Delay for tarpit
        return paramiko.AUTH_FAILED  # Always reject authentication

# Function to handle individual connections
def handle_persistent_tarpit(client_socket, client_address):
    print(f"[+] Connection from {client_address}")
    transport = None
    active_connections.append(client_socket)  # Track the socket
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)

        server = PersistentTarpitSSHServer()
        transport.start_server(server=server)

        while transport.is_active() and not stop_event.is_set():  # Keep connection alive while the server is running
            try:
                time.sleep(10)  # Artificial delay to trap the attacker
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
                client_thread = Thread(target=handle_persistent_tarpit, args=(client_socket, client_address))
                client_thread.setDaemon(True)  # Ensure threads exit properly
                client_thread.start()
    except Exception as e:
        if not stop_event.is_set():
            print(f"[-] Error in server loop: {e}")
    finally:
        server_socket.close()
        print("[+] Server has been stopped.")

if __name__ == "__main__":
    start_persistent_tarpit()
