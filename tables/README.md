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

To unzip a zip file to a folder

```python
def unzip_file(file: str, dest: str: pwd: str = None) -> None:
    """
    Unzips `file` to an output folder `dest`
    """
    with zipfile.ZipFile(file, 'r') as f:
        if isinstance(pwd, str):
            f.extractall(dest, pwd=bytes(pwd, 'utf-8'))
        else:
            f.extractall(dest)
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

### 1.7 Replace column with one-hot-encoded columns

One-hot encode columns with: `pd.get_dummies(df)`, `df[col].str.get_dummies()`

```python
def create_dummies_fn(series: pd.Series,
                      new_columns: Dict[int, str]) -> pd.DataFrame:
    return pd.get_dummies(series).rename(
        columns=new_columns
    })

def replace_column_with_dummies(df: pd.DataFrame,
                                column_to_replace: str,
                                new_columns: Dict[int, str],
                                create_dummies_fn: Callable[..., pd.DataFrame]) -> pd.DataFrame:
    df_dummies = create_dummies_fn(df[column_to_replace], new_columns)
    return pd.concat(
        (df.drop(columns=[col]), df_dummies),
        axis=1
    )
```

### 1.8 Columns with only a single value

To list all the columns with only a single unique value:

```python
unique_cols = df.apply(pd.Series.nunique)
unique_cols = unique_cols.index[unique_cols == 1]
print(','.join(list(unique_cols)))
```

To list columns with `n` unique values, replace `unique_cols == 1` with `unique_cols == n`

To plot the number of unique values per column and
their frequency:

```python
def plot_barh(df: pd.DataFrame, col: str, cmap: str = 'tab10', **kwargs) -> None:
    df_data = df[col].value_counts()
    _, ax = plt.subplots(1, 1, figsize=(8,len(vc)/3.5))
    cmap = plt.cm.get_cmap(cmap, len(df_data)).colors
    df_data.plot.barh(
        color=cmap, grid=True, title=col, ax=ax, **kwargs)
    for i, (_, label) in enumerate(df_data.iteritems()):
        ax.annotate(f'{label}', xy=(label+1, i-0.1), color='blue');
    ax.grid(True)
    ax.set_title(col)
    ax.set_xlabel('Counts')
    ax.set_ylabel('Value')
```

### 1.9 Quantile-based discretisation

```python
import numpy as np
import pandas as pd

x = np.random.uniform(0, 1, 20)
df = pd.DataFrame({'x': x})
df['c1'] = pd.qcut(x, q=4)  # returns the actual intervals as the labels
df['c2'] = pd.qcut(x, q=4, labels=np.arange(4))  # use labels 1,2,3,4
df['c3'] = pd.qcut(x, q=3, labels=['lo','mid','hi'])
```

```python
>>> df.sort_values('x')
           x               c1 c2   c3
1   0.020729  (0.0197, 0.149]  0   lo
7   0.126949  (0.0197, 0.149]  0   lo
13  0.128471  (0.0197, 0.149]  0   lo
8   0.134889  (0.0197, 0.149]  0   lo
6   0.139756  (0.0197, 0.149]  0   lo
9   0.152104   (0.149, 0.243]  1   lo
15  0.166057   (0.149, 0.243]  1   lo
14  0.173742   (0.149, 0.243]  1  mid
3   0.187096   (0.149, 0.243]  1  mid
0   0.201927   (0.149, 0.243]  1  mid
18  0.285001    (0.243, 0.61]  2  mid
10  0.356298    (0.243, 0.61]  2  mid
19  0.426361    (0.243, 0.61]  2  mid
4   0.430289    (0.243, 0.61]  2   hi
11  0.589490    (0.243, 0.61]  2   hi
12  0.670398    (0.61, 0.974]  3   hi
5   0.825376    (0.61, 0.974]  3   hi
16  0.835593    (0.61, 0.974]  3   hi
17  0.944898    (0.61, 0.974]  3   hi
2   0.974342    (0.61, 0.974]  3   hi
```

### 1.10 Correlation Matrix

To obtain the correlation matrix for a dataframe

```python
df = df.drop(columns=...)  # Optionally remove columns that aren't needed
df.corr().style.background_gradient(cmap='RdBu', axis=None).set_precision(3)
```

### 1.11 Histogram

To get a grid of histograms for each column of a dataframe

```python
df.hist()
```

### 1.12 Profiling

To use Pandas Profiler, for output within a Jupyter Notebook

```python
from pandas_profiling import ProfileReport

profile = ProfileReport(df, title="Report Title", explorative=True, minimal=False)
profile.to_notebook_iframe()
```
