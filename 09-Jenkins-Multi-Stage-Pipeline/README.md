Name: Anantha Chary C M
USN: 1BM23IS025

# Lab 09: Jenkins Multi-Stage Pipeline — Build, Test & Deploy a Python App

## Objective

Create and run a **multi-stage Jenkins Pipeline** for a Python Flask application that performs five stages:

1. **Build** — Dependency installation step (echo placeholder in this exercise)
2. **Test** — Run unit tests with `unittest`
3. **Deploy** — Copy the application to a mock deployment directory
4. **Run Application** — Start Flask in the background
5. **Test Application** — Run the tests against the deployed copy

| Component           | Tool          | Purpose                                       |
| ------------------- | ------------- | --------------------------------------------- |
| **CI Server**       | Jenkins (LTS) | Run the multi-stage pipeline job              |
| **Version Control** | GitHub        | Host the Flask app and `Jenkinsfile`          |
| **Pipeline Plugin** | Pipeline      | Enable declarative pipeline syntax in Jenkins |
| **Language**        | Python 3      | Flask application and unit tests              |

---

## Prerequisites

| Tool                | Purpose                                       |
| ------------------- | --------------------------------------------- |
| **Jenkins**         | Running at `http://localhost:8080` (Lab 07)   |
| **GitHub account**  | To host the application repository            |
| **Git**             | Installed locally                             |
| **Pipeline plugin** | Installed with the suggested plugins (Lab 07) |

> **Important:** Start Jenkins if needed: `docker start jenkins`.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Lab 09 Pipeline Workflow                        │
│                                                                  │
│  ┌──────────┐    git push     ┌──────────────────┐              │
│  │  Local    │ ──────────────►│  GitHub           │              │
│  │  Machine  │                │  devops-sample-   │              │
│  │           │                │  code repo        │              │
│  └──────────┘                └────────┬─────────┘              │
│                                        │                         │
│                                  git clone                       │
│                                        │                         │
│                                        ▼                         │
│                               ┌──────────────────┐              │
│                               │  Jenkins (Docker) │              │
│                               │                   │              │
│                               │  Pipeline Stages: │              │
│                               │  1. Build         │              │
│                               │  2. Test          │              │
│                               │  3. Deploy        │              │
│                               │  4. Run App       │              │
│                               │  5. Test App      │              │
│                               └──────────────────┘              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Part A: Prepare the Python Flask Application

### Step 1: Create the Application Files

Create a project directory:

```bash
mkdir python-flask-app
cd python-flask-app
```

Create `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    app.run(debug=True)
```

Create `requirements.txt`:

```
flask==2.1.2
```

Create `test_app.py`:

```python
import unittest
from app import app

class TestApp(unittest.TestCase):
    def test_home(self):
        tester = app.test_client()
        response = tester.get("/")
        print(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "Hello, Jenkins Multi-Stage Pipeline!")

if __name__ == "__main__":
    unittest.main()
```

> 📸 **Screenshot:** `01_app_files.png` — `app.py`, `requirements.txt`, `test_app.py`

---

### Step 2: Create the Jenkinsfile

Create `Jenkinsfile` in the same directory:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m unittest discover -s .'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                mkdir -p ${WORKSPACE}/python-app-deploy
                cp ${WORKSPACE}/app.py ${WORKSPACE}/python-app-deploy/
                '''
            }
        }
        stage('Run Application') {
            steps {
                echo 'Running application...'
                sh '''
                nohup python3 ${WORKSPACE}/python-app-deploy/app.py > ${WORKSPACE}/python-app-deploy/app.log 2>&1 &
                echo $! > ${WORKSPACE}/python-app-deploy/app.pid
                '''
            }
        }
        stage('Test Application') {
            steps {
                echo 'Testing application...'
                sh '''
                python3 ${WORKSPACE}/test_app.py
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}
```

> **Note:**
>
> - **Build** — only prints a message in this exercise. A real pipeline would run `pip install -r requirements.txt` here
> - **Test** — `unittest discover` finds and runs `test_app.py`
> - **Deploy** — creates `${WORKSPACE}/python-app-deploy` and copies `app.py` into it
> - **Run Application** — starts Flask with `nohup`, writes the PID file
> - **Test Application** — reruns the tests; they use Flask's `test_client()`, so they pass whether or not the background server bound a port
> - **post** — success/failure message after all stages

> 📸 **Screenshot:** `02_jenkinsfile.png` — `Jenkinsfile` content

---

## Part B: Push to GitHub

### Step 3: Push Everything to GitHub

> **Note:** Reusing the Lab 08 repository (recommended) — copy the four files into that clone and:
>
> ```bash
> git add app.py requirements.txt test_app.py Jenkinsfile
> git commit -m "Added Flask app and Jenkinsfile"
> git push
> ```

For a **new repository**:

```bash
git init
git add .
git commit -m "Initial commit with Flask app and Jenkinsfile"
git branch -M main
git remote add origin https://github.com/<your-GitHub-username>/devops-sample-code.git
git push -u origin main
```

> **Important:** `git branch -M main` matters on a fresh `git init`: the default branch is `master` and `git push -u origin main` fails with _src refspec main does not match any_.

> 📸 **Screenshot:** `03_git_push.png` — `git push` output

---

## Part C: Prepare the Jenkins Container

### Step 4: Install Python and Flask Inside the Jenkins Container

The `jenkins/jenkins:lts` image has no Python. Install it as **root**:

```bash
docker exec -it -u root jenkins bash
```

Inside the container:

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv python3-flask
python3 --version
python3 -c "import flask; print(flask.__version__)"
exit
```

> **Important:** Install Flask with **`apt-get install -y python3-flask`**, not `pip3 install flask`. The image is Debian 12, whose Python is marked externally managed, so pip aborts with:
>
> ```
> error: externally-managed-environment
> × This environment is externally managed
> ```
>
> If you must use pip: `pip3 install flask --break-system-packages`.

> 📸 **Screenshot:** `04_install_python.png` — Python and Flask installed inside the Jenkins container

---

## Part D: Create and Run the Pipeline Job

### Step 5: Create the Pipeline Job

1. Open `http://localhost:8080` → **New Item**
2. Name: `Python-MultiStage-Pipeline`
3. Select **Pipeline** → **OK**

> 📸 **Screenshot:** `05_new_pipeline.png` — New Item page with Pipeline selected

---

### Step 6: Configure the Pipeline

In the job configuration:

1. **Pipeline** section
2. **Definition:** `Pipeline script from SCM`
3. **SCM:** `Git`
4. **Repository URL:** `https://github.com/<your-username>/devops-sample-code.git`
5. **Credentials:** add Username + PAT if the repo is private
6. **Branch Specifier:** `*/main`
7. **Script Path:** `Jenkinsfile`
8. **Save**

> **Note:** **Alternative:** choose `Pipeline script` and paste the Jenkinsfile directly. Useful for quick tests and prototyping, but the job is then not under source control.

> 📸 **Screenshot:** `06_pipeline_config.png` — Pipeline → SCM configuration

---

### Step 7: Run the Pipeline

Click **Build Now**. The **Stage View** shows one column per stage — Build, Test, Deploy, Run Application, Test Application.

> 📸 **Screenshot:** `07_stage_view.png` — Stage View with all five stages green

---

### Step 8: View the Console Output

Build **#1** → **Console Output**.

**Expected output:**

```
Started by user admin
Obtained Jenkinsfile from git https://github.com/<your-username>/devops-sample-code.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/Python-MultiStage-Pipeline
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
Selected Git installation does not exist. Using Default
The recommended git tool is: NONE
No credentials specified
 > git rev-parse --resolve-git-dir /var/jenkins_home/workspace/Python-MultiStage-Pipeline/.git # timeout=10
Fetching changes from the remote Git repository
 > git fetch --tags --force --progress -- https://github.com/<your-username>/devops-sample-code.git +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git rev-parse refs/remotes/origin/main^{commit} # timeout=10
Checking out Revision f82e59e16ad6e72100e54d776df07dd26edf80de (refs/remotes/origin/main)
Commit message: "Added Jenkinsfile"
[Pipeline] }
[Pipeline] // stage
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Build)
[Pipeline] echo
Creating virtual environment and installing dependencies...
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Test)
[Pipeline] echo
Running tests...
[Pipeline] sh
+ python3 -m unittest discover -s .
.
----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
Hello, Jenkins Multi-Stage Pipeline!
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Deploy)
[Pipeline] echo
Deploying application...
[Pipeline] sh
+ mkdir -p /var/jenkins_home/workspace/Python-MultiStage-Pipeline/python-app-deploy
+ cp /var/jenkins_home/workspace/Python-MultiStage-Pipeline/app.py /var/jenkins_home/workspace/Python-MultiStage-Pipeline/python-app-deploy/
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Run Application)
[Pipeline] echo
Running application...
[Pipeline] sh
+ echo 5064
+ nohup python3 /var/jenkins_home/workspace/Python-MultiStage-Pipeline/python-app-deploy/app.py
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Test Application)
[Pipeline] echo
Testing application...
[Pipeline] sh
+ python3 /var/jenkins_home/workspace/Python-MultiStage-Pipeline/test_app.py
.
----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
Hello, Jenkins Multi-Stage Pipeline!
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] echo
Pipeline completed successfully!
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS
```

> **Important:** The key lines are `Ran 1 test ... OK` and `Pipeline completed successfully!` followed by `Finished: SUCCESS`.

> 📸 **Screenshot:** `08_console_output.png` — full Console Output ending in `Finished: SUCCESS`

---

## Part E: Handling Build Errors

### Step 9: Troubleshooting Build Failures

The first run normally fails on missing Python/dependencies. Get into the container as root and install them:

```bash
docker ps -a | grep jenkins
docker exec -it -u root jenkins bash
```

Inside the container:

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv python3-flask
python3 -m unittest discover -s .
exit
```

#### Error: `python3: not found`

```bash
docker exec -it -u root jenkins bash -c "apt-get update && apt-get install -y python3 python3-pip"
```

#### Error: `ModuleNotFoundError: No module named 'flask'`

```bash
docker exec -it -u root jenkins bash -c "apt-get install -y python3-flask"
```

#### Error: `externally-managed-environment` from pip

Use the apt package above, or:

```bash
docker exec -it -u root jenkins bash -c "pip3 install flask --break-system-packages"
```

Then **Build Now** again.

> 📸 **Screenshot:** `09_build_fix.png` — the error, the fix, and the successful rebuild

---

## Part F: Additional Enhancements (Optional)

### 10a. Code Quality Stage

Install the linter in the container first:

```bash
docker exec -it -u root jenkins bash -c "apt-get install -y flake8"
```

Add before `Test` in the Jenkinsfile:

```groovy
stage('Code Quality') {
    steps {
        echo 'Running code quality checks...'
        sh 'flake8 .'
    }
}
```

> **Note:** `flake8` exits non-zero on any finding, which fails the build. To report without failing: `sh 'flake8 . || true'`, or add a `setup.cfg` with `[flake8]` / `max-line-length = 120`.

### 10b. Deploy to a Docker Container

```groovy
stage('Dockerize') {
    steps {
        sh '''
        docker build -t flask-pipeline-app ${WORKSPACE}
        docker rm -f flask-pipeline-app 2>/dev/null || true
        docker run -d --name flask-pipeline-app -p 5000:5000 flask-pipeline-app
        '''
    }
}
```

Requires the Docker CLI and `/var/run/docker.sock` mounted into the Jenkins container.

### 10c. Notifications

```groovy
post {
    success {
        mail to: 'you@example.com',
             subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
             body: "Pipeline completed successfully. ${env.BUILD_URL}"
    }
    failure {
        mail to: 'you@example.com',
             subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
             body: "Pipeline failed. See ${env.BUILD_URL}console"
    }
}
```

Configure SMTP under **Manage Jenkins → System → E-mail Notification** (or use the Slack Notification plugin).

> 📸 **Screenshot:** `10_enhancements.png` — Code Quality stage in the Stage View (optional)

---

## Deployment Evidence

### Application Files

![Application Files](Screenshots/01_app_files.png)

### Jenkinsfile

![Jenkinsfile](Screenshots/02_jenkinsfile.png)

### Git Push

![Git Push](Screenshots/03_git_push.png)

### Install Python in Jenkins Container

![Install Python](Screenshots/04_install_python.png)

### New Pipeline Item

![New Pipeline](Screenshots/05_new_pipeline.png)

### Pipeline Configuration

![Pipeline Config](Screenshots/06_pipeline_config.png)

### Stage View

![Stage View](Screenshots/07_stage_view.png)

### Console Output

![Console Output](Screenshots/08_console_output.png)

---

## Verification Summary

| Item                        | Expected Value                                                       |
| --------------------------- | -------------------------------------------------------------------- |
| **GitHub Repo**             | `app.py`, `test_app.py`, `requirements.txt`, `Jenkinsfile` on `main` |
| **Jenkins Job**             | `Python-MultiStage-Pipeline` (Pipeline)                              |
| **Pipeline Source**         | SCM → Git → repo URL, Script Path `Jenkinsfile`                      |
| **Container Prerequisites** | `python3`, `python3-pip`, `python3-venv`, `python3-flask` installed  |
| **Stage: Build**            | ✅ Echo message                                                      |
| **Stage: Test**             | ✅ `Ran 1 test ... OK`                                               |
| **Stage: Deploy**           | ✅ `app.py` in `${WORKSPACE}/python-app-deploy/`                     |
| **Stage: Run Application**  | ✅ Flask started with `nohup`, PID written                           |
| **Stage: Test Application** | ✅ `Ran 1 test ... OK`                                               |
| **Post Action**             | `Pipeline completed successfully!`                                   |
| **Build Status**            | `Finished: SUCCESS`                                                  |

---

## Cleanup (after submission)

```bash
# In the Jenkins UI: Python-MultiStage-Pipeline → Delete Project

# Optional
docker stop jenkins
```

---

## Troubleshooting

| Problem                                        | Solution                                                                                             |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `python3: not found`                           | `docker exec -it -u root jenkins bash -c "apt-get update && apt-get install -y python3 python3-pip"` |
| `ModuleNotFoundError: No module named 'flask'` | `apt-get install -y python3-flask` inside the container                                              |
| `error: externally-managed-environment`        | Use the apt package, or `pip3 install flask --break-system-packages`                                 |
| Pipeline can't find `Jenkinsfile`              | Script Path must be exactly `Jenkinsfile` (case-sensitive) and at the repo root                      |
| `src refspec main does not match any`          | `git branch -M main`, then push                                                                      |
| `Couldn't find any revision to build`          | Branch Specifier is `*/master` — set `*/main`                                                        |
| Git clone fails                                | Check the URL; add Username+PAT credentials for a private repo                                       |
| Stage View shows a red stage                   | Click the stage → **Logs** for the exact error                                                       |
| `nohup` app not running                        | Read `${WORKSPACE}/python-app-deploy/app.log` for the Python traceback                               |
| `flake8` fails the build                       | `sh 'flake8 . \|\| true'`, or configure `max-line-length` in `setup.cfg`                             |

---

## Quick Reference: Complete Command Sequence

```bash
# Step 1-2: app files + Jenkinsfile
mkdir python-flask-app && cd python-flask-app

cat > app.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > requirements.txt << 'EOF'
flask==2.1.2
EOF

cat > test_app.py << 'EOF'
import unittest
from app import app

class TestApp(unittest.TestCase):
    def test_home(self):
        tester = app.test_client()
        response = tester.get("/")
        print(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "Hello, Jenkins Multi-Stage Pipeline!")

if __name__ == "__main__":
    unittest.main()
EOF

cat > Jenkinsfile << 'EOF'
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m unittest discover -s .'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                mkdir -p ${WORKSPACE}/python-app-deploy
                cp ${WORKSPACE}/app.py ${WORKSPACE}/python-app-deploy/
                '''
            }
        }
        stage('Run Application') {
            steps {
                echo 'Running application...'
                sh '''
                nohup python3 ${WORKSPACE}/python-app-deploy/app.py > ${WORKSPACE}/python-app-deploy/app.log 2>&1 &
                echo $! > ${WORKSPACE}/python-app-deploy/app.pid
                '''
            }
        }
        stage('Test Application') {
            steps {
                echo 'Testing application...'
                sh '''
                python3 ${WORKSPACE}/test_app.py
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}
EOF

# 📸 01_app_files.png
# 📸 02_jenkinsfile.png

# Step 3: push to GitHub
git init && git add . && git commit -m "Initial commit with Flask app and Jenkinsfile"
git branch -M main
git remote add origin https://github.com/<your-username>/devops-sample-code.git
git push -u origin main
# 📸 03_git_push.png

# Step 4: Python + Flask inside Jenkins (apt, NOT pip)
docker exec -it -u root jenkins bash
# apt-get update && apt-get install -y python3 python3-pip python3-venv python3-flask
# exit
# 📸 04_install_python.png

# Steps 5-6: pipeline job
# New Item → "Python-MultiStage-Pipeline" → Pipeline
# Pipeline script from SCM → Git → repo URL → */main → Jenkinsfile
# 📸 05_new_pipeline.png
# 📸 06_pipeline_config.png

# Steps 7-8: build and verify
# Build Now → Stage View → Console Output
# 📸 07_stage_view.png
# 📸 08_console_output.png

# Step 9: fix build errors if any, rebuild
# 📸 09_build_fix.png

# Step 10 (optional): Code Quality / Dockerize / notifications
# 📸 10_enhancements.png
```
