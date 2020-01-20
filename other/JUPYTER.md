# Jupyter Notebooks

## 1. Conversion

### 1.1 Help

To get help, type:

```bash
jupyter nbconvert --help
```

### 1.2 Jupyter Notebook Conversion

```bash
jupyter nbconvert --execute my_note --to htmlbook.ipynb
jupyter nbconvert my_notebook.ipynb --to html
jupyter nbconvert my_notebook.ipynb --to python
```

## 2. Export Options

### 2.1 Formats (`--to` option)

- `asciidoc`, `custom`, `html`, `latex`, `markdown`, `notebook`,
  `pdf`, `python`, `rst`, `script`, `slides`

### 2.2 Templates (`--template` option)

- **LaTeX**: `base`, `article`, `report`
- **HTML**: `basic`, `full`

