# PYTHON SETUP

## 1. UV

### 1.1 UV Python build on Amazon Linux 2023 with Bash autocompletion

```bash
sudo dnf install -y git gcc g++ 
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ "$SHELL" = "/bin/bash" ]; then
  echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
  echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
fi
```

### 1.2 UV Python build on Mac OS X with Zsh autocompletion

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ "$SHELL" = "/bin/zsh" ]; then
  echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
  echo 'eval "$(uvx --generate-shell-completion zsh)"' >> ~/.zshrc
fi
```

### 1.3 UV Init

```bash
uv init
uv python install 3.13
uv add setuptools wheel
uv add --script myscripy.py "boto3"
```

### 1.4 UV Unnstallation

```bash
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
```


## 2. Anaconda

### 2.1 Update

```bash
conda update -n base conda
conda update --all
conda update anaconda
conda install python=3.13
```

### 2.2 Disabling Anaconda

To prevent Anaconda from loading the base environment on startup

```bash
conda config --set auto_activate_base false
```

## 3. Virtualenv

```bash
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install virtualenv
cd ~
python3 -m virtualenv venv
source venv/bin/activate
```

## 4. Pyenv

Install pyenv and a specific Python version

```bash
curl https://pyenv.run | bash
# pyenv install --list | grep " 3\.11"  # To see available versions
pyenv install -v 3.11.9
```

Create an environment in pyenv and activate it

```bash
pyenv virtualenv 3.11.9 venv
pyenv activate venv
```

Go to a folder and set the environment for that folder

```bash
cd /path/to/folder/
pyenv local venv
pip install package1 package2 package3
```
