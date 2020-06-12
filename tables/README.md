# Tables

## 1. Pandas

### 1.1 [Pandas Options](https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html):

```python
pd.set_option('precision', 5)
pd.set_option('colheader_justify', 'left')
pd.set_option('max_colwidth', 300)
pd.set_option('max_rows', 100)
```

Setting and reverting the maximum number of rows in a dataframe

```python
pd.set_option('display.max_rows', 999)
pd.reset_option('display.max_rows')
```

### 1.2 [Creating Dataframes](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)

```python
df = pd.DataFrame(columns=['a', 'b', 'c'])  # Empty Dataframe
df = pd.DataFrame(
    data=[['X', 'Y', 'Z'],
          ['1', '2', '3'],
          ['i', 'j', 'k']],
    columns=['a', 'b', 'c'], index=[1, 2, 3])
```

### 1.3 Exploding a column

#### 1.3.1 Exploding into rows

```python
df = pd.DataFrame({'A': ['1, 2, 3', 'X, Y', 'ZZZ'], 'B': [-1, -2, -3]})
df.A = df.A.str.split(',')
```

```python
>>> print(df.explode('A))
     A  B
0    1 -1
0    2 -1
0    3 -1
1    X -2
1    Y -2
2  ZZZ -3
```

#### 1.3.2 Exploding into columns

```python
df = pd.DataFrame({
    'Pet': ['Dog', 'Cat'],
    'DOB': ['2020-04-03', '2020-05-04']
})
```

```python
df_DOB = df.DOB.str.split('-', expand=True)
df['Year'] = df_DOB[0]
df['Month'] = df_DOB[1]
df['Day'] = df_DOB[2]
```

```
>>> print(df)
   Pet         DOB  Year Month Day
0  Dog  2020-04-03  2020    04  03
1  Cat  2020-05-04  2020    05  04
```
