# SSH Tarpit

An SSH tarpit implemented in Python using `paramiko` to trap and slow down brute-force attacks by keeping connections open and delaying interactions.

## Features

- **Simulated SSH Server**: Uses a fake SSH server to handle incoming SSH connection attempts.
- **Connection Persistence**: Keeps connections alive indefinitely or until the server is stopped.
- **Login Attempt Logging**: Logs every login attempt with the username and password used.
- **Artificial Delays**: Introduces delays in authentication and interactions to frustrate attackers.
- **Graceful Shutdown**: Allows for clean termination of the server and all active connections using `Ctrl+C`.

## Requirements

- Python 3.x
- `paramiko` library

Install `paramiko` using pip if it is not already installed:
```bash
pip install paramiko
```

## Usage

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### Run the Server
```bash
python3 ssh_tarpit.py
```

### Connect to the Tarpit
Using an SSH client, connect to the tarpit server:
```bash
ssh -p 2222 <any-username>@<server-ip>
```
- Use any username and password.
- The server will log the login attempt and artificially delay the response.

### Stop the Server
Press `Ctrl+C` to gracefully stop the server:
```bash
[!] Stopping server...
[+] Server has been stopped.
```

## File Overview

- `ssh_tarpit.py`: The main script to run the SSH tarpit server.

## How It Works

1. The server simulates an SSH interface using `paramiko`.
2. All incoming connection attempts are delayed to slow down brute-force attacks.
3. Connections are kept alive indefinitely until the server is stopped or the attacker disconnects.
4. All login attempts (username and password) are logged in the terminal for analysis.

## Notes

- **Legal Considerations**: Ensure you have permission to deploy this tarpit. Use it only in environments where you are authorized to monitor and trap SSH traffic.
- **Security**: Deploy this tarpit on a secured environment, such as a virtual machine or isolated network.

## Example Output

### Server Startup
```bash
[+] SSH Tarpit running on 0.0.0.0:2222
```

### Connection Attempt
```bash
[+] New connection from ('127.0.0.1', 54321)
[!] Login attempt: user:password
[+] Keeping connection to ('127.0.0.1', 54321) active...
```

### Server Shutdown
```bash
[!] Stopping server...
[+] Server has been stopped.
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Feel free to open issues or submit pull requests if you have ideas for improvement or additional features.

