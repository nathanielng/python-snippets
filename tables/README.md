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

### 1.4 Reading / Writing Data

#### 1.4.1 CSV files

Reading from CSV files

```python
df = pd.read_csv(csv_file)
df = pd.read_csv(csv_file, delimiter=None, header='infer', names=None, index_col=None, usecols=None, dtype=None, skiprows=None, nrows=None, na_values=None, parse_dates=False, date_parser=None, comment=None, delim_whitespace=False, ...)
```

To write to a CSV file, with the index dropped

```python
df.to_csv(csv_file, index=False)
```

#### 1.4.2 Zip files

To read in a csv that is inside a zip file

```python
import pandas as pd
import zipfile

with zipfile.ZipFile('my_file.zip') as z:
    files = [ f.filename for f in z.filelist]
    print('\n'.join(files))
    df = pd.read_csv(
        z.extract('file_to_extract.csv', path='folder_to_extract/'),
    )
```

#### 1.4.3 Excel files

To read in the first sheet of a single Excel file

```python
xl_file = 'filename.xlsx'
df = pd.read_excel(xl_file)
```

To read in multiple sheets of an Excel file

```python
with pd.ExcelFile(xl_file) as f:
    df1 = pd.read_excel(f, sheet_name='Sheet1')
    df2 = pd.read_excel(f, sheet_name='Sheet2')
    ...
```

To write to a single Excel file, with the index dropped:

```python
df.to_excel(xl_file, index=False)
```

To write multiple Pandas DataFrames to an Excel file:

```python
with pd.ExcelWriter(xl_file) as f:
    df1.to_excel(f, 'Sheet1')
    df2.to_excel(f, 'Sheet2')
    ...
```

### 1.5 Finding NAs

To return the count and fraction of NAs in a Pandas DataFrame

```python
def find_NAs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return the count and fraction of NAs in a DataFrame
    """
    n = len(df)
    NAs = df.isna().sum()
    NAs = NAs[NAs > 0].sort_values(ascending=False)
    return pd.DataFrame({
        'Count': NAs.values,
        'Fraction': NAs.values / n
    }, index=NAs.index)
```

### 1.6 Duplicated Rows

```python
def get_duplicated_rows(df):
    return df[df.duplicated(keep='first')]

def count_duplicated_rows(df):
    return df.duplicated(keep='first').sum()

def drop_duplicated_rows(df):
    return df[~df.duplicated(keep='first')]
```

### 1.7 Correlation Matrix

To obtain the correlation matrix for a dataframe

```python
df = df.drop(columns=...)  # Remove all the columns that you don't need
correlation_matrix = df.corr()
```
