Name: Anantha Chary C M
USN: 1BM23IS025

# Lab 05: Docker Security with AppArmor and Python

## Objective
Secure Docker containers using **AppArmor profiles** to restrict access to sensitive directories (`/etc/`, `/var/`), prevent execution of unauthorized binaries (`/bin/bash`), apply security policies using the Docker SDK for Python, and test/verify restricted actions inside the container.

---

## Environment Setup
* **OS:** Windows 11 Home Single Language (running **WSL 2 — Ubuntu**)
* **Container Runtime:** Docker Desktop (with WSL 2 integration enabled)
* **CLI Tools:** `docker`, `apparmor_parser`, `aa-status`
* **Language:** Python 3.x with Flask
* **Application:** Python Flask web app (port `5000`)

> **Note:** AppArmor is a Linux-only security module. All commands in this lab are executed inside WSL 2 (Ubuntu).

---

## Concept: AppArmor & Container Security

**What is AppArmor?**
AppArmor (Application Armor) is a Linux kernel security module that enforces **mandatory access control (MAC)** policies. It confines programs to a limited set of resources by defining what files, directories, network capabilities, and system calls a process can access.

**Why use AppArmor with Docker?**

| Aspect | Without AppArmor | With AppArmor |
|--------|-----------------|---------------|
| File Access | Container can read `/etc/passwd`, system configs | ❌ Blocked by profile rules |
| Binary Execution | `/bin/bash`, `/bin/sh` freely accessible | ❌ Denied execution |
| Network | Unrestricted | ✅ Only allowed protocols (e.g., TCP for Flask) |
| System Capabilities | `sys_admin` and others available | ❌ Explicitly denied |

**Real-Life Use Case — Production Container Hardening:**
- A Flask web application serves HTTP traffic but should **never** read system configuration files or spawn shell processes
- AppArmor profiles enforce the **principle of least privilege** — the container can only do what it needs to
- Even if an attacker exploits a vulnerability in the app, they cannot escalate privileges or access sensitive host data

---

## Architecture

```
┌─────────────── AppArmor Profile (my-apparmor-profile) ───────────────┐
│                                                                       │
│  ALLOW:                          DENY:                                │
│  ✅ /app/** (rwk)                ❌ /etc/** (read)                    │
│  ✅ network inet stream          ❌ /var/** (read/write)              │
│  ✅ capability net_bind_service  ❌ /bin/** (execute)                 │
│                                  ❌ /usr/bin/** (execute)             │
│                                  ❌ capability sys_admin              │
│                                                                       │
│  ┌─────────────────────────────────────────┐                         │
│  │  Flask Container (flask-secure)         │                         │
│  │  Image: flask-apparmor                  │                         │
│  │  Port: 5000                             │                         │
│  │  Security: --security-opt=apparmor=...  │                         │
│  └─────────────────────────────────────────┘                         │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Execution

### 1. Install AppArmor Utilities
```bash
sudo apt-get update
sudo apt-get install -y apparmor-utils
```

Verify AppArmor is active:
```bash
sudo aa-status
```
* **Status:** List of loaded AppArmor profiles displayed with their modes (enforce/complain).

### 2. Create the Flask Application
```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 3. Create the Dockerfile
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install flask
EXPOSE 5000
CMD ["python", "app.py"]
```

### 4. Build the Docker Image
```bash
docker build -t flask-apparmor .
docker images | grep flask-apparmor
```
* **Status:** Image `flask-apparmor:latest` built successfully.

### 5. Baseline Test — Without AppArmor

Run the container without any security restrictions to establish a baseline:
```bash
docker run -d --name flask-test -p 5000:5000 flask-apparmor
```

Test that the app works:
```bash
curl http://localhost:5000
```
**Expected:** `Hello, this is a secure Flask application running inside a Docker container!`

Test that sensitive actions are currently **allowed** (no security):
```bash
# Read sensitive file (should succeed without AppArmor)
docker exec flask-test cat /etc/passwd

# Execute bash (should succeed without AppArmor)
docker exec flask-test /bin/bash -c "echo 'bash works'"
```
* **Status:** Both commands succeed — this is the **insecure baseline**.

Stop and remove the test container:
```bash
docker stop flask-test && docker rm flask-test
```

### 6. Create the AppArmor Profile

Save the following profile to `/etc/apparmor.d/my-apparmor-profile`:
```bash
sudo nano /etc/apparmor.d/my-apparmor-profile
```

Profile content:
```
#include <tunables/global>

/usr/bin/python3 {
    # Deny access to sensitive system files
    deny /etc/** r,
    deny /var/** rw,

    # Allow Flask app to bind to port 5000
    network inet stream,

    # Permissions to the application directory
    /app/** rwk,

    # Deny execution of any binaries in /bin or /usr/bin
    deny /bin/** rmix,
    deny /usr/bin/** rmix,

    # Capability restrictions
    capability net_bind_service,
    deny capability sys_admin,
}
```

**Profile Breakdown:**

| Rule | Effect |
|------|--------|
| `deny /etc/** r` | Blocks reading any files under `/etc/` (e.g., `/etc/passwd`) |
| `deny /var/** rw` | Blocks reading/writing under `/var/` |
| `network inet stream` | Allows TCP networking (needed for Flask) |
| `/app/** rwk` | Allows read/write/lock access to the app directory |
| `deny /bin/** rmix` | Blocks executing binaries in `/bin/` |
| `deny /usr/bin/** rmix` | Blocks executing binaries in `/usr/bin/` |
| `capability net_bind_service` | Allows binding to network ports |
| `deny capability sys_admin` | Blocks system admin capabilities |

### 7. Load the AppArmor Profile
```bash
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
sudo aa-status | grep my-apparmor-profile
```
* **Status:** Profile `my-apparmor-profile` appears in the list of loaded profiles.

### 8. Run the Container WITH AppArmor Profile
```bash
docker run -d --name flask-secure \
  --security-opt="apparmor=my-apparmor-profile" \
  -p 5000:5000 \
  flask-apparmor
```

**Flags explained:**
- `--security-opt="apparmor=my-apparmor-profile"` → Apply the AppArmor profile to the container
- `-p 5000:5000` → Map container port to host

```bash
docker ps
```
* **Status:** Container `flask-secure` running with AppArmor profile applied.

### 9. Test Restricted Actions (Manual)

Test the same sensitive actions — they should now be **blocked** by AppArmor:
```bash
# Attempt to read /etc/passwd (should be DENIED)
docker exec flask-secure cat /etc/passwd

# Attempt to execute /bin/bash (should be DENIED)
docker exec flask-secure /bin/bash -c "echo 'bash works'"
```

**Expected output:**
```
cat: /etc/passwd: Permission denied
OCI runtime exec failed: ... permission denied
```

Verify the Flask app still works:
```bash
curl http://localhost:5000
```
**Expected:** `Hello, this is a secure Flask application running inside a Docker container!`

* **Key Observation:** The AppArmor profile successfully blocks sensitive actions while allowing the Flask application to run normally. This is **mandatory access control** in action.

Stop and remove:
```bash
docker stop flask-secure && docker rm flask-secure
```

### 10. Apply AppArmor Profile via Docker SDK for Python

Install the Docker SDK:
```bash
pip install docker
```

Run the Python script:
```bash
python apply_apparmor.py
```

```python
# apply_apparmor.py
import docker

client = docker.from_env()

print("Building image from Dockerfile...")
client.images.build(path=".", tag="flask-apparmor")

print("Running container with AppArmor profile...")
container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")

container_info = client.api.inspect_container(container.id)
apparmor_profile = container_info['HostConfig']['SecurityOpt']
print(f"AppArmor profile applied: {apparmor_profile}")

print("Stopping the container...")
container.stop()
print("Container stopped.")
```

**Expected output:**
```
Building image from Dockerfile...
Running container with AppArmor profile...
Container started: f8c2a7f9
AppArmor profile applied: ['apparmor=my-apparmor-profile']
Stopping the container...
Container stopped.
```

### 11. Test Restricted Actions with Python Script

```bash
python test_restricted_actions.py
```

```python
# test_restricted_actions.py
import docker

client = docker.from_env()

print("Starting container with AppArmor profile...")
container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")
print("\n--- Testing Restricted Actions ---")

exit_code, output = container.exec_run("cat /etc/passwd")
print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode()}")

exit_code, output = container.exec_run("/bin/bash")
print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode()}")

print("\nStopping the container...")
container.stop()
print("Container stopped.")
```

**Expected output:**
```
Starting container with AppArmor profile...
Container started: f8c2a7f9

--- Testing Restricted Actions ---
Attempt to read /etc/passwd: Exit Code 1, Output:
Attempt to execute /bin/bash: Exit Code 126, Output:

Stopping the container...
Container stopped.
```

* **Exit Code 1** for `cat /etc/passwd` → Permission denied (AppArmor blocked file read)
* **Exit Code 126** for `/bin/bash` → Permission denied (AppArmor blocked binary execution)

---

## Deployment Evidence

### AppArmor Installation & Status
![AppArmor Install](Screenshots/01_apparmor_install.png)

### Flask Application
![Flask App](Screenshots/02_flask_app.png)

### Dockerfile
![Dockerfile](Screenshots/03_dockerfile.png)

### Docker Build
![Docker Build](Screenshots/04_docker_build.png)

### Baseline Test (Without AppArmor)
![Baseline Test](Screenshots/05_baseline_test.png)

### AppArmor Profile
![AppArmor Profile](Screenshots/06_apparmor_profile.png)

### Load Profile
![Load Profile](Screenshots/07_load_profile.png)

### Container With AppArmor
![Container With AppArmor](Screenshots/08_container_with_apparmor.png)

### Restricted Actions Test
![Restricted Actions](Screenshots/09_restricted_actions.png)

### Apply AppArmor via Python SDK
![Apply AppArmor Python](Screenshots/10_apply_apparmor_py.png)

### Test Restricted Actions via Python
![Test Restricted Python](Screenshots/11_test_restricted_py.png)

---

## Verification Summary

| Item | Expected Value |
|------|---------------|
| **Docker Image** | `flask-apparmor:latest` |
| **AppArmor Profile** | `my-apparmor-profile` loaded |
| **Flask App** | Responds at `http://localhost:5000` |
| **Read `/etc/passwd`** | ❌ Blocked (Exit Code 1) |
| **Execute `/bin/bash`** | ❌ Blocked (Exit Code 126) |
| **Network Access** | ✅ Allowed (Flask serves HTTP) |
| **App Directory Access** | ✅ Allowed (`/app/**` readable) |
| **Docker SDK Script** | Successfully applies and verifies profile |

---

## Cleanup

```bash
# Stop and remove any running containers
docker stop flask-secure flask-test 2>/dev/null
docker rm flask-secure flask-test 2>/dev/null

# Remove the Docker image
docker rmi flask-apparmor

# (Optional) Remove the AppArmor profile
sudo rm /etc/apparmor.d/my-apparmor-profile
sudo apparmor_parser -R /etc/apparmor.d/my-apparmor-profile 2>/dev/null

# Verify cleanup
docker ps -a
docker images | grep flask-apparmor
```

---

## Viva Questions & Answers

1. **What is the purpose of using AppArmor with Docker containers?**
   AppArmor is used to enforce security policies and confine applications to a limited set of resources. With Docker containers, it helps to limit access to system resources, files, and networks, thus providing an additional layer of security.

2. **How do AppArmor profiles help secure a Docker container?**
   AppArmor profiles define what a containerized application can or cannot do. They restrict access to sensitive directories, network capabilities, file execution, and system calls, ensuring the container behaves securely without affecting the host system.

3. **Why is it important to restrict access to sensitive directories such as `/etc/` and `/var/`?**
   Sensitive directories like `/etc/` contain configuration files and sensitive information such as user data and system settings. Restricting access prevents the container from reading or modifying important system files, reducing the risk of security breaches.

4. **What other capabilities can you restrict using AppArmor profiles?**
   AppArmor can restrict a container's ability to access the network, bind to specific ports, execute binaries, write to specific directories, and use system administration capabilities (`cap_sys_admin`).

5. **How can you verify if an AppArmor profile is successfully applied to a Docker container?**
   You can verify if an AppArmor profile is applied by inspecting the container using the Docker SDK or the Docker CLI. The `HostConfig.SecurityOpt` field will show the applied security options, including the AppArmor profile name.
