# Tips

## Dictionaries

1. Combine dictionaries `d1`, `d2` into `d3`:
   `d3 = {**d1, **d2}`

## Pandas

1. [Pandas Options](https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html):

```python
pd.set_option('precision', 5)
pd.set_option('max_colwidth', 300)
pd.set_option('colheader_justify', 'left')
```

Setting and reverting the maximum number of rows in a dataframe

```python
pd.set_option('display.max_rows', 999)
pd.reset_option('display.max_rows')
```

2. [Creating Dataframes](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)

```python
df = pd.DataFrame(columns=['a', 'b', 'c'])  # Empty Dataframe
df = pd.DataFrame(
    data=[['X', 'Y', 'Z'],
          ['1', '2', '3'],
          ['i', 'j', 'k']],
    columns=['a', 'b', 'c'], index=[1, 2, 3])
```