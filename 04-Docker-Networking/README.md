Name: Anantha Chary C M
USN: 1BM23IS025

# Lab 04: Docker Networking with Multi-Container Application

## Objective

Understand Docker networking concepts by configuring a multi-container application with a Flask REST API, MySQL database, and Redis cache — all communicating over a custom bridge network.

---

## Environment Setup

- **OS:** Windows 11 Home Single Language
- **Container Runtime:** Docker Desktop
- **CLI Tools:** `docker`
- **Application:** Python Flask REST API (port `5001`)

---

## Concept: Docker Bridge Networking

**Why custom bridge networks?**

| Feature            | Default Bridge                     | Custom Bridge (`my-bridge-net`)      |
| ------------------ | ---------------------------------- | ------------------------------------ |
| Container name DNS | ❌ Not supported                   | ✅ Automatic DNS resolution          |
| Isolation          | Shared with all default containers | Only explicitly connected containers |
| Communication      | Must use IP addresses              | Use container names directly         |

**Real-Life Use Case — Microservice Architecture:**

- **Web server** (Flask) communicates with a **database** (MySQL) and a **cache** (Redis)
- Each service runs in its own isolated container
- Containers discover each other by **name** instead of fragile IP addresses
- The custom bridge network acts as a private LAN for your microservices

---

## Architecture

```
┌──────────────────── my-bridge-net (Custom Bridge) ────────────────────┐
│                                                                       │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐         │
│  │  Flask API    │    │    MySQL      │    │    Redis      │         │
│  │  (flask-api)  │◄──►│  (mysql)      │    │  (redis)      │         │
│  │  Port: 5001   │    │  Port: 3306   │    │  Port: 6379   │         │
│  └───────┬───────┘    └───────────────┘    └───────────────┘         │
│          │                                                            │
└──────────┼────────────────────────────────────────────────────────────┘
           │ -p 5001:5001
           ▼
     Host: localhost:5001
```

---

## Step-by-Step Execution

### 1. Create a Custom Bridge Network

```powershell
docker network create --driver bridge my-bridge-net
```

- **Status:** Network `my-bridge-net` created — returns a network ID hash.

### 2. Verify the Network

```powershell
docker network ls
```

- **Status:** `my-bridge-net` listed with driver `bridge` and scope `local`.

### 3. Inspect the Network (Empty)

```powershell
docker network inspect my-bridge-net
```

- **Status:** Network details shown — subnet `172.19.0.0/16`, gateway `172.19.0.1`, empty `Containers` field (no containers connected yet).

### 4. Create the Flask Application

```python
# app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "This is a simple REST API built with Flask."
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

**Dependencies (`requirements.txt`):**

```
Flask==2.0.1
Werkzeug<3.0
```

### 5. Create the Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
CMD ["python", "app.py"]
```

### 6. Build the Flask Docker Image

```powershell
docker build -t flask-api .
docker images | Select-String flask-api
```

- **Status:** Image `flask-api:latest` built successfully.

### 7. Launch All Three Containers on the Bridge Network

```powershell
# Launch MySQL container
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=root123 mysql:latest

# Launch Redis container
docker run -d --name redis --net=my-bridge-net redis:latest

# Launch Flask container (with port mapping)
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api
```

**Flags explained:**

- `-d` → Detached mode (background)
- `--net=my-bridge-net` → Connect to the custom bridge network
- `-p 5001:5001` → Map Flask container port to host
- `-e MYSQL_ROOT_PASSWORD=root123` → Required MySQL environment variable

```powershell
docker ps
```

- **Status:** All 3 containers (`flask`, `mysql`, `redis`) running on `my-bridge-net`. The screenshot shows the `docker run` commands pulling MySQL and Redis images, followed by `docker ps` confirming running containers.

### 8. Test the Flask API

```powershell
curl http://localhost:5001/about
```

**Expected response:**

```json
{
  "description": "This is a simple REST API built with Flask.",
  "name": "Simple REST API",
  "version": "1.0"
}
```

- **Status:** Flask API accessible from host via `localhost:5001`.

### 9. Test Container-to-Container Connectivity

```powershell
docker exec -it flask bash
```

Inside the Flask container:

```bash
# Ping MySQL container by name
ping mysql

# Ping Redis container by name
ping redis

exit
```

- **Status:** Ping to MySQL resolved to `172.19.0.2` (10 packets, 0% loss, avg `0.190 ms`). Ping to Redis resolved to `172.19.0.3` (10 packets, 0% loss, avg `0.184 ms`). Docker DNS successfully resolves container names on the custom bridge network.

### 10. Cleanup

```powershell
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net

# Verify
docker ps -a
docker network ls
```

- **Status:** All containers stopped and removed. Network `my-bridge-net` deleted. Verification shows no containers running and `my-bridge-net` no longer listed in networks.

---

## Deployment Evidence

### Create Network

![Create Network](Screenshots/01_create_network.png)

### Network List

![Network List](Screenshots/02_network_ls.png)

### Network Inspect (Empty)

![Network Inspect](Screenshots/03_network_inspect.png)

### Docker Build

![Docker Build](Screenshots/04_docker_build.png)

### Launch Containers & Docker PS

![Containers Running](Screenshots/05_containers_running.png)

### Ping MySQL (Container-to-Container)

![Ping MySQL](Screenshots/06_ping_mysql.png)

### Ping Redis (Container-to-Container)

![Ping Redis](Screenshots/07_ping_redis.png)

### Cleanup

![Cleanup](Screenshots/08_cleanup.png)

---

## Verification Summary

| Item                   | Expected Value                        |
| ---------------------- | ------------------------------------- |
| **Network Name**       | `my-bridge-net`                       |
| **Network Driver**     | `bridge`                              |
| **Flask Container**    | Running on port `5001`                |
| **MySQL Container**    | Running on port `3306`                |
| **Redis Container**    | Running on port `6379`                |
| **Flask → MySQL Ping** | Successful (via container name)       |
| **Flask → Redis Ping** | Successful (via container name)       |
| **Flask API Response** | JSON at `http://localhost:5001/about` |

---

## Cleanup

```powershell
# Stop and remove all three containers
docker stop mysql redis flask
docker rm mysql redis flask

# Remove the custom network
docker network rm my-bridge-net

# Verify cleanup
docker ps -a
docker network ls
```

- **Verified:** No containers found in `docker ps -a`, and `my-bridge-net` no longer appears in `docker network ls`.

---
