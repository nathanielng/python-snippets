# Python Examples

## 1. Loops and Iterators

### 1.1 Zip

**Code**

```python
a = ['a', 'b', 'c', 'd', 'e']
b = [3, 1, 4, 1, 6]
for x, y in zip(a, b):
    print(f"{x} = {y}")
```

**Output**

```python
a = 3
b = 1
c = 4
d = 1
e = 6
```

### 1.2 Dictionaries

**Code**

```python
d = dict(zip(a,b))
print(d)
for k, v in d.items():
    print(f"{k}: {v}")
```

**Output**

```python
{'a': 3, 'b': 1, 'c': 4, 'd': 1, 'e': 6}
a: 3
b: 1
c: 4
d: 1
e: 6
```

