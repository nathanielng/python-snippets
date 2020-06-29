# Python

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

## 4. Functools

### 4.1 Partials

```python
from functools import partial

def my_function(x, a):
    return x + a

# Same as my_function(), but a = 2:
new_function = partial(my_function, 2)

# This assertion should be true
assert new_function(100) == 102
```

## 5. Jupyter Notebooks

### 5.1 IPython magic - selected commands

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
