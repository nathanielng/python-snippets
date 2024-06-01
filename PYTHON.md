# Python

## 0. Setup

Get Python version

```bash
python -c "import sys; print(sys.version)"
```

### 0.1 Setup virtualenv

```bash
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install virtualenv
cd ~
python3 -m virtualenv venv
source venv/bin/activate
```


### 0.2 Setup pyenv


```bash
curl https://pyenv.run | bash
# pyenv install --list | grep " 3\.11"  # To see available versions
pyenv install -v 3.11.9
pyenv virtualenv 3.11.9 venv
```

```bash
cd /path/to/folder/
pyenv local venv
pip install package1 package2 package3
```


### 0.3 SageMaker & HuggingFace `requirements.txt` setup

```bash
cat > requirements.txt << EOF
accelerate
einops
huggingface_hub[cli]
optimum
sentencepiece
sagemaker
torch
transformers
EOF
pip install -U pip
pip install -r requirements.txt
```

```bash
pip install --disable-pip-version-check -q exlibrary1==x.x.0
pip uninstall -y --disable-pip-version-check exlibrary1==x.xx.1 exlibrary2==0.x.1 --quiet
```


## 1. Lists

1. Check that two lists, `l1`, `l2` are the same:
   `assert set(l1) == set(l2)`

## 2. Dictionaries

1. Combine dictionaries `d1`, `d2` into `d3`:
   `d3 = {**d1, **d2}`

## 3. Type Hinting

### 3.1 Declarations

```python
from typing import Dict, List, Optional, Set, Tuple
from typing import Callable, Iterator, Union
```

### 3.2 Functions

Examples (basic types)

```python
def my_function(my_int: int, my_float: float=0.0, my_string: Optional[str]=None, **kwargs):
    pass
```

Examples (tuples and dictionaries)

```python
def my_function(xy: Tuple[int, int]=(0, 0), d: Dict[str, np.ndarray]):
    pass
```


## 4. Strings

### 4.1 Handling Unicode

```python
from unidecode import unidecode

def convert_unicode(text):
    return unidecode(text)

def remove_unicode(text):
    return text.encode("ascii", "ignore")
```

### 4.2 Counting Tokens

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
def get_token_count(text):
    return len(encoding.encode(text))
```


## 5. Functools

### 5.1 Partials

```python
from functools import partial

def my_function(x, a):
    return x + a

# Same as my_function(), but a = 2:
new_function = partial(my_function, 2)

# This assertion should be true
assert new_function(100) == 102
```


## 6. Jupyter Notebooks

### 6.1 IPython magic - selected commands

```python
%cd
%debug
%env
%load_ext
%lsmagic
%matplotlib inline
%pip install [package]
%precision
%time
%timeit
%who, %whos, %who_ls
%xmode
```

```python
%%bash
%%html
%%javascript
%%latex
%%perl
%%ruby
%%svg
%%writefile [-a] filename
```

### 6.2 Jupyter Extensions

```bash
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
```


# Anaconda Python

## 1. Update

```bash
conda update -n base conda
conda update --all
conda update anaconda
conda install python=3.9
```

## 2. Disabling Anaconda

To prevent Anaconda from loading the base environment on startup

```bash
conda config --set auto_activate_base false
```
