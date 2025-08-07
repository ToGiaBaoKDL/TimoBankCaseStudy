# TimoBankCaseStudy – Deploy Dagster on AWS EC2

## 📌 Overview

This guide helps you deploy the `TimoBankCaseStudy` project using [Dagster](https://dagster.io/) on an AWS EC2 instance with `systemd` for managing services.

You will:

- Install Python 3.11
- Set up a virtual environment
- Configure Dagster
- Deploy both Dagster web server and daemon as systemd services
- Pull updates via GitHub

---

## 📦 System Requirements

| Component            | Details                  |
|---------------------|--------------------------|
| OS                  | Amazon Linux 2 / Ubuntu 20.04+ |
| Python              | 3.11+                    |
| Git                 | For pulling code         |
| Open Port           | `3000` (for Dagster Web UI) |

---

## 🔧 Install Required Packages

### For Amazon Linux 2:
```bash
sudo yum update -y
sudo yum install git gcc make zlib-devel bzip2 bzip2-devel readline-devel \
sqlite sqlite-devel wget curl unzip libffi-devel xz-devel openssl-devel -y
```

### For Ubuntu:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git build-essential zlib1g-dev libbz2-dev libreadline-dev \
libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl -y
```

## 🐍 Install Python 3.11
```bash
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz
sudo tar xzf Python-3.11.8.tgz
cd Python-3.11.8
sudo ./configure --enable-optimizations
sudo make altinstall

# Confirm
python3.11 --version
```

## 🔗 Clone the GitHub Project
```bash
cd ~
git clone https://github.com/ToGiaBaoKDL/TimoBankCaseStudy.git
cd TimoBankCaseStudy
```

## 🔐 Create .env File (for Database Connection)
Run the following in terminal (modify values accordingly):
```bash
cat <<EOF > .env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=your_db_host
DB_PORT="5432"
EOF
```

## 🧪 Set Up Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🗂️ Configure Dagster
```bash
mkdir -p ~/TimoBankCaseStudy/dagster_home
export DAGSTER_HOME=~/TimoBankCaseStudy/dagster_home
echo "export DAGSTER_HOME=~/TimoBankCaseStudy/dagster_home" >> ~/.bashrc
```

## 🌐 Test Local Launch
```bash
dagster dev -f dags_or_jobs/bank_dq_dags.py
```
Visit http://<EC2-PUBLIC-IP>:3000 to access the UI.

## 🧹 Create SWAP (if lack of RAM)
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

## ⚙️ Create systemd Services
### 1. `dagster.service` – Dagster Web Server
```bash
sudo nano /etc/systemd/system/dagster.service
```
Paste the following:
```ini
[Unit]
Description=Dagster Web UI
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/TimoBankCaseStudy
Environment="DAGSTER_HOME=/home/ec2-user/TimoBankCaseStudy/dagster_home"
ExecStart=/home/ec2-user/TimoBankCaseStudy/.venv/bin/dagster webserver -h 0.0.0.0 -p 3000 -f dags_or_jobs/bank_dq_dags.py
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. `dagster-daemon.service` – Dagster Daemon
```bash
sudo nano /etc/systemd/system/dagster-daemon.service
```
Paste the following:
```ini
[Unit]
Description=Dagster Daemon
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/TimoBankCaseStudy
Environment="DAGSTER_HOME=/home/ec2-user/TimoBankCaseStudy/dagster_home"
ExecStart=/home/ec2-user/TimoBankCaseStudy/.venv/bin/dagster-daemon run --working-directory /home/ec2-user/TimoBankCaseStudy
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## 🔁 Reload & Start Services
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable dagster.service
sudo systemctl enable dagster-daemon.service

sudo systemctl start dagster.service
sudo systemctl start dagster-daemon.service
```

## ✅ Check Status
```bash
sudo systemctl status dagster.service
sudo systemctl status dagster-daemon.service
```

## 🔁 After Pulling Code from GitHub
```bash
cd ~/TimoBankCaseStudy
git pull origin master

# Then restart services
sudo systemctl restart dagster.service
sudo systemctl restart dagster-daemon.service
```

## 🛠️ Troubleshooting
- If services fail to start, check logs with journalctl.
- Make sure ExecStart paths match your project structure and virtual environment.

## 📎 Optional Improvements
- Add `post-receive` or `git pull && restart` automation
- Add HTTPS using Nginx + Certbot.
- Set up SSH deploy keys for CI/CD.