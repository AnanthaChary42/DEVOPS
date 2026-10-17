# DEVOPS

Name: Anantha Chary C M
USN: 1BM23IS025

---

## Repository Structure

This repository contains DevOps lab experiments organized. Each lab folder includes its own **`README.md`** with a detailed explanation — covering the objective, architecture, step-by-step instructions, and screenshots.

```
DEVOPS/
├── 00-Portfolio/
├── 01-Nginx-Pod/
├── 02-Flask-K8s/
├── 03-Minikube-Scaling/
├── 04-Docker-Networking/
├── 05-Docker-Security-AppArmor/
├── 06-Grafana-Realtime-Monitoring/
├── 07-Jenkins-CI-Automation/
├── 08-Jenkins-Hello-World-Job/
├── 09-Jenkins-Multi-Stage-Pipeline/
└── README.md  ← You are here
```

---

## Labs Overview

| #   | Folder                                                                | Topic                                                           | Key Files                                                                               |
| --- | --------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 00  | [`00-Portfolio`](./00-Portfolio/)                                     | Portfolio website deployed via GitHub Pages                     | `index.html`, `resume.pdf`                                                              |
| 01  | [`01-Nginx-Pod`](./01-Nginx-Pod/)                                     | Deploy & Expose Nginx Pod on Kubernetes (Minikube)              | —                                                                                       |
| 02  | [`02-Flask-K8s`](./02-Flask-K8s/)                                     | Deploy a Flask App on Kubernetes using Minikube & YAML          | `app.py`, `Dockerfile`, `flask-deployment.yaml`                                         |
| 03  | [`03-Minikube-Scaling`](./03-Minikube-Scaling/)                       | Scaling Flask App on Kubernetes using ReplicaSets               | `app.py`, `Dockerfile`, `flashsale-replicaset.yaml`                                     |
| 04  | [`04-Docker-Networking`](./04-Docker-Networking/)                     | Docker Networking with Multi-Container Application              | `app.py`, `Dockerfile`, `requirements.txt`                                              |
| 05  | [`05-Docker-Security-AppArmor`](./05-Docker-Security-AppArmor/)       | Docker Security with AppArmor and Python                        | `app.py`, `Dockerfile`, `apply_apparmor.py`, `test_restricted_actions.py`               |
| 06  | [`06-Grafana-Realtime-Monitoring`](./06-Grafana-Realtime-Monitoring/) | Real-Time Monitoring with Prometheus & Grafana (Quick Commerce) | `delivery_metrics.py`, `Dockerfile`, `Jenkinsfile`, `prometheus.yml`, `alert_rules.yml` |
| 07  | [`07-Jenkins-CI-Automation`](./07-Jenkins-CI-Automation/)             | Introduction to CI and Jenkins Installation (Docker)            | —                                                                                       |
| 08  | [`08-Jenkins-Hello-World-Job`](./08-Jenkins-Hello-World-Job/)         | Creating a "Hello World" Jenkins Freestyle Job                  | `hello-world.sh`                                                                        |
| 09  | [`09-Jenkins-Multi-Stage-Pipeline`](./09-Jenkins-Multi-Stage-Pipeline/) | Jenkins Multi-Stage Pipeline — Build, Test & Deploy             | `app.py`, `test_app.py`, `requirements.txt`, `Jenkinsfile`                              |

---

## How Each Lab Folder Is Organized

Every lab folder follows a consistent structure:

```
XX-Lab-Name/
├── README.md          # Detailed explanation, steps, and architecture
├── Screenshots/       # Output screenshots and demo images
├── app.py             # Application source code (where applicable)
├── Dockerfile         # Container build instructions
└── *.yaml / *.yml     # Kubernetes manifests or config files
```

- **`README.md`** — The primary reference for each lab. It includes the objective, tools used, architecture diagram, complete walkthrough, and screenshots demonstrating the output.
- **`Screenshots/`** — Contains all captured screenshots referenced in the README.
- **Source & Config files** — Application code (`app.py`), container definitions (`Dockerfile`), Kubernetes manifests (`.yaml`), and tool-specific configs (`prometheus.yml`, `alert_rules.yml`, etc.).

> **📖 To understand any lab, start by reading the `README.md` inside that lab's folder.**
