# SSH Tarpit with Extended PostgreSQL Logging

An SSH tarpit implemented in Python using **Paramiko**. This script traps and slows down brute-force attacks by artificially delaying SSH authentication attempts and never granting access. It logs various data to **PostgreSQL** in three separate tables:

1. **`login_attempts`** – IP, port, username, and password for each attempt.  
2. **`harvested_credentials`** – Only username and password, plus a timestamp.  
3. **`ip_access`** – Logs only the IP address and a timestamp when a connection arrives.

---

## Features

- **Simulated SSH Server**: Uses a fake SSH server to handle incoming SSH connections.
- **Connection Persistence**: Maintains connections indefinitely or until the server is stopped.
- **Multiple PostgreSQL Tables**:
  - **`login_attempts`**: Full details of login attempts.
  - **`harvested_credentials`**: Minimal credentials-only storage.
  - **`ip_access`**: Tracks IP address upon connection.
- **Config-Driven**: Loads database credentials from a local `config.json` file.
- **Graceful Shutdown**: Stops cleanly with `Ctrl+C`, terminating all active connections.

---

## Requirements

1. **Python 3.x**  
2. **Paramiko** and **Psycopg2** libraries:
    ```bash
    pip install paramiko psycopg2
    ```
3. **PostgreSQL** server with the following tables:

### Database Setup

```sql
-- 1) Full login attempts
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(50),
    port INTEGER,
    username VARCHAR(100),
    password VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2) Harvested credentials (username/password only)
CREATE TABLE IF NOT EXISTS harvested_credentials (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) IP access log (only IP and timestamp)
CREATE TABLE IF NOT EXISTS ip_access (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(50),
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Configuration

Create a file named `config.json` (excluded from Git with `.gitignore`) in the project folder. It should look like this:

```json
{
    "host": "localhost",
    "port": 5432,
    "database": "ssh_tarpit",
    "user": "myuser",
    "password": "mypassword"
}
```

Adjust the values as needed to match your PostgreSQL setup.

---

## Usage

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Create and Edit `config.json`**:
    ```bash
    cp config.example.json config.json
    # Edit config.json to match your PostgreSQL credentials
    ```

3. **Install Dependencies**:
    ```bash
    pip install paramiko psycopg2
    ```

4. **Run the SSH Tarpit**:
    ```bash
    python3 main.py
    ```
    You should see:
    ```
    [+] SSH Tarpit running on 0.0.0.0:2222
    ```

5. **Test the Tarpit**:
    - From another machine or terminal:
      ```bash
      ssh -p 2222 anyuser@<your-ip-or-hostname>
      ```
    - Provide any password; the script will:
      - Record an **IP-only entry** in `ip_access`.
      - Store the **full attempt** in `login_attempts` (IP, port, username, password).
      - Store only **credentials** in `harvested_credentials` (username, password).

6. **Stop the Tarpit**:
    - Press `Ctrl + C` in the terminal running the script.
    - You should see:
      ```
      [!] Stopping server...
      [+] Server has been stopped.
      ```

---

## Verifying Logs in PostgreSQL

You can verify your logs with commands like:

```sql
-- 1) Full login attempts
SELECT * FROM login_attempts;

-- 2) Harvested credentials
SELECT * FROM harvested_credentials;

-- 3) IP access logs
SELECT * FROM ip_access;
```

---

## Security Considerations

- This tarpit is designed for **research and defensive security** purposes. Always ensure you have permission to run such a service on your network or system.
- Deploy it in an **isolated environment** (e.g., a VM or a dedicated server) since it is deliberately attracting malicious traffic.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

