# Search

## 1. Finding files in a folder recursively

### 1.1 Finding filenames that match a pattern

```bash
find path/to/folder -name 'my_example_pattern'
```

Example (find all `.py` files in current folder)

```bash
find ./ -name '*.py'
```

### 1.2 Finding patterns in text files

```bash
grep -iInr path/to/folder -e 'my_example_pattern' --color=auto
```

**Flags**

- `-i` (case insensitive), 
- `-I` (ignore binary files)
- `-n` (show line number of match),
- `-r` (recurse into subdirectories)
- `-w` (search for whole words)

