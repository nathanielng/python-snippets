# Python

## 1. Type Hinting

### 1.1 Declarations

```python
from typing import Dict, List, Optional, Set, Tuple
from typing import Callable, Iterator, Union
```

### 1.2 Functions

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

## 2. Jupyter Notebooks

### 2.1 IPython magic - selected commands

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