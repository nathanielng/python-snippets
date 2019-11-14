# Machine Learning Datasets

## 1. Scikit Learn Datasets

- [`load_boston()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html#sklearn.datasets.load_boston) - Boston House Prices Dataset (*regression*)
- [`load_iris()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html#sklearn.datasets.load_iris) - Iris Dataset (*classification*)
- [`load_diabetes()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html#sklearn.datasets.load_diabetes) - Diabetes Dataset (*regression*)
- [`load_digits()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html#sklearn.datasets.load_digits) - Digits Dataset (*classification*)
- [`load_linnerud()`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_linnerud.html#sklearn.datasets.load_linnerud) - Linnerud Dataset (*multivariate regression*)

## 2. Seaborn Datasets

- [`seaborn.load_dataset`](https://seaborn.pydata.org/generated/seaborn.load_dataset.html)`(name, cache=True, data_home=None, **kws)`


## 3. Pydataset

- https://github.com/iamaziz/PyDataset

**Example Code**

```python
from pydataset import data
boston = data('boston')
iris = data('iris')
```

To see list of available datasets:

```python
data()
```