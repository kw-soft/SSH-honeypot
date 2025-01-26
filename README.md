# SSH Tarpit

An SSH tarpit implemented in Python using `paramiko` to trap and slow down brute-force attacks by keeping connections open and delaying interactions. All login attempts are logged in a PostgreSQL database.

## Features

- **Simulated SSH Server**: Uses a fake SSH server to handle incoming SSH connection attempts.
- **Connection Persistence**: Keeps connections alive indefinitely or until the server is stopped.
- **Login Attempt Logging**: Logs every login attempt with the username, password, and client IP in a PostgreSQL database.
- **Artificial Delays**: Introduces delays in authentication and interactions to frustrate attackers.
- **Graceful Shutdown**: Allows for clean termination of the server and all active connections using `Ctrl+C`.

## Requirements

- Python 3.x
- `paramiko` library
- `psycopg2` library

Install the required libraries using pip:

```bash
pip install paramiko psycopg2
```

## Database Setup

1. Install PostgreSQL and create a database:

   ```bash
   sudo -u postgres psql
   CREATE DATABASE ssh_tarpit;
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ssh_tarpit TO your_user;
   ```

2. Create a `config.json` file in the project directory with the following content:

   ```json
   {
       "host": "localhost",
       "port": 5432,
       "database": "ssh_tarpit",
       "user": "your_user",
       "password": "your_password"
   }
   ```

3. Run the server to ensure it connects and logs correctly:

   ```bash
   python3 ssh_tarpit.py
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
- The server will log the login attempt to the database and artificially delay the response.

### Stop the Server

Press `Ctrl+C` to gracefully stop the server:

```bash
[!] Stopping server...
[+] Server has been stopped.
```

## File Overview

- `ssh_tarpit.py`: The main script to run the SSH tarpit server.
- `config.json`: Configuration file for database connection details (not included in the repository).

## How It Works

1. The server simulates an SSH interface using `paramiko`.
2. All incoming connection attempts are delayed to slow down brute-force attacks.
3. Connections are kept alive indefinitely until the server is stopped or the attacker disconnects.
4. All login attempts (username, password, and IP) are logged in a PostgreSQL database for later analysis.

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

### Database Log

Example entry in the PostgreSQL database:

```
 id |    ip      | port  | username |  password   |      timestamp      
----+------------+-------+----------+-------------+---------------------
 1  | 127.0.0.1  | 54321 | user     | password123 | 2025-01-26 15:00:00
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

