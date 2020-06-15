# Machine Learning Datasets

## 1. Scikit Learn Datasets

### 1.1 Import

```
import sklearn.datasets
```

### 1.2 Subroutines

- [`load_boston()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html#sklearn.datasets.load_boston) - Boston House Prices Dataset (*regression*)
- [`load_iris()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html#sklearn.datasets.load_iris) - Iris Dataset (*classification*)
- [`load_diabetes()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html#sklearn.datasets.load_diabetes) - Diabetes Dataset (*regression*)
- [`load_digits()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html#sklearn.datasets.load_digits) - Digits Dataset (*classification*)
- [`load_linnerud()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_linnerud.html#sklearn.datasets.load_linnerud) - Linnerud Dataset (*multivariate regression*)
- [`fetch_openml()`](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_openml.html) - multiple OpenML datasets.
  Specify desired dataset with: `name=` or `data_id=`.

## 2. Seaborn Datasets

- [`seaborn.load_dataset`](https://seaborn.pydata.org/generated/seaborn.load_dataset.html)`(name, cache=True, data_home=None, **kws)`


## 3. Pydataset

- **Github**: https://github.com/iamaziz/PyDataset

### 3.1 Available Datasets

To load a Pandas Dataframe of the available datasets:

```python
df = data()
df.head()
```

### 3.2 Example Code

```python
from pydataset import data
boston = data('boston')
iris = data('iris')
titanic = data('titanic')
```
