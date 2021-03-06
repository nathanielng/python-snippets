# Scikit-Learn

## 1. Machine Learning

### 1.1 Load the data

Load the data into a Pandas dataframe using `pd.read_csv()` or `pd.read_excel()`,
with the first column specified as the index column (optional).  For large
datasets, `df.sample()` may be used to use only a fraction of the dataset
for the initial debugging.

```python
import pandas as pd

df = pd.read_csv('file.csv', index_col=0)
df = pd.read_excel('file.xlsx', index_col=0)

# Optional sampling
df.sample(frac=0.05, inplace=True, replace=False, random_state=123)  # based on fraction
df.sample(n=5000, inplace=True, replace=False, random_state=123)     # based on rows
```

Split dataframe in to `X` and `y` using the last column, or by specifying a
specific target column:

```python
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

X = df.loc[:, df.columns != target_col]
y = df.loc[:, target_col]
```

### 1.2 Split data into training & testing sets

`X` and `y` may be split into training & test sets using `train_test_split`.
This method also works with dataframes.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, random_state=123)

df_train, df_test = train_test_split(
    df, test_size=0.2, shuffle=True, random_state=123)
```

### 1.3 Build basic model

#### 1.3.1 Build a basic classifier

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier()
rf.fit(X_train, y_train)
```

#### 1.3.2 Build a basic regressor

```python
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor()
rf.fit(X_train, y_train)
```

### 1.4 Score model without cross validation

```python
from sklearn.metrics import r2_score

y_pred = rf.predict(X_test)
score = r2_score(y_test, y_pred)
```

### 1.5 Score model with cross validation

```python
from sklearn.metrics import make_scorer, r2_score
from sklearn.model_selection import cross_val_score, cross_validate

scorer = make_scorer(r2_score, greater_is_better=True)
cv_score = cross_val_score(rf, X_train, y_train, scoring=scorer, cv=5).mean()
```

```python
cv_results = pd.DataFrame(cross_validate(
    rf, X_train, y_train,
    scoring=('r2', 'neg_mean_squared_error'),
    return_train_score=True,
    cv=5))
```

### 1.6 Hyperparameter search with cross validation

To perform a grid search:

```python
from sklearn.model_selection import GridSearchCV

print(rf.get_params())  # view default parameters
parameters = {
    'n_estimators': [200, 400, 800, 1200],
    'max_features': ['auto', 'sqrt'],
    'max_depth': [10, 20, 50, 100, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

clf = GridSearchCV(rf, parameters)
```

To perform a randomised search:

```python
from scipy.stats import uniform
from sklearn.model_selection import RandomizedSearchCV
from sklearn.utils.fixes import loguniform

parameters = {
    'n_estimators': [int(x) for x in np.linspace(start=200, stop=2000, num=10)],
    'max_features': ['auto', 'sqrt'],
    'max_depth': [int(x) for x in np.linspace(10, 110, num=11), None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}
clf = RandomizedSearchCV(rf, parameters)
```

To perform the hyperparameter search and to obtain the best parameters

```python
clf.fit(X_train, y_train)
print(clf.best_params_)
```

### 1.7 Model Pipeline with hyperparameter search

**Code**

```python
from sklearn import preprocessing
from sklearn.compose import TransformedTargetRegressor
from sklearn.datasets import load_diabetes
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR

RANDOM_STATE = 1234

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=RANDOM_STATE)
n_samples = len(y)

pipe = Pipeline(steps=[
    ('QT', preprocessing.QuantileTransformer(random_state=RANDOM_STATE)),
    ('SVR', SVR())
])

parameters = {
    'QT__n_quantiles': [n_samples, n_samples//2, n_samples//4],
    'SVR__C': [.05, .5, 1, 4, 8, 16, 32],
    'SVR__kernel': ['linear', 'rbf', 'poly'],
    'SVR__gamma': ['scale', 'auto']
}

clf = GridSearchCV(
    pipe,
    param_grid=parameters,
    cv=5,
    n_jobs=4,
    scoring='r2',
    verbose=0,
    refit=True
)

clf.fit(X_train, y_train)
y_pred1 = clf.predict(X_train)
train_err = r2_score(y_train, y_pred1)

y_pred2 = clf.predict(X_test)
test_err = r2_score(y_test, y_pred2)
print(f'Error: {train_err:.4f} (training), {test_err:.4f} (test)')
print(f'Best parameters: {clf.best_params_}')
```

**Output**

```python
Error: 0.6021 (training), 0.4430 (test)
Best parameters: {'QT__n_quantiles': 221, 'SVR__C': 32, 'SVR__gamma': 'scale', 'SVR__kernel': 'rbf'}
```