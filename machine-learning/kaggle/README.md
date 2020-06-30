# Kaggle

## 1. Kaggle API

### 1.1 Setup

Download `kaggle.json` from your account at:
https://www.kaggle.com/yourkaggleusername/account

Copy the file as follows:

```bash
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

Install the Kaggle Python package as follows

```bash
pip install kaggle
```

### 1.2 Usage

#### 1.2.1 Kaggle Competitions

```bash
kaggle competitions [list|files|download|leaderboard|...]
```

#### 1.2.2 Kaggle Config

```bash
kaggle config [view|set|unset]
```

#### 1.2.3 Datasets

```bash
kaggle datasets [list|files|download|...]
```

#### 1.2.4 Kaggle Kernels

```bash
kaggle kernels [list|init|status|...]
```

