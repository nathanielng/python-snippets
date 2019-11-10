# Python Debugging

## 1. Debugging using PDB

### 1.1 Using `breakpoint()`

Add the following line to stop code execution at a specific point
in Python source code.

```python
breakpoint()
```

In versions of Python earlier than 3.7, use `import pdb; pdb.set_trace()`.

### 1.2 From the command line

```
python -m pdb myscript.py arg1 arg2
```

## 2. Debugging in a Jupyter notebook

After an error has occurred, type `%debug` in a Jupyter notebook cell
to get the `ipdb>` debug prompt.

Alternatively, add the following to any code block:

```python
from IPython.core.debugger import set_trace
set_trace()
```

The import statement can be at the beginning of the code.
The `set_trace()` statement should be at the location where
you wish to set your breakpoint


## 3. References

This document uses information from the following sources:

- https://realpython.com/python-debugging-pdb/
- https://medium.com/@chrieke/jupyter-tips-and-tricks-994fdddb2057

Other debugging options

- [PixieDebugger](https://www.analyticsvidhya.com/blog/2018/07/pixie-debugger-python-debugging-tool-jupyter-notebooks-data-scientist-must-use/)

