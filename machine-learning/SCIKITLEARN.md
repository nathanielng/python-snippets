# Scikit-Learn

## 1. Machine Learning

### 1.1 Load the data

```python
import pandas as pd

df = pd.read_csv('file.csv', index_col=0)
df.sample(frac=0.01, inplace=True, random_state=123)  # optional sampling
X = df.iloc[:, :-1]
y = df.iloc[:, -1]
```

### 1.2 Split data into training & testing sets

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, random_state=123)
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
from sklearn.model_selection import cross_val_score, cross_val_predict

scorer = make_scorer(r2_score, greater_is_better=True)
cv_score = cross_val_score(rf, X_train, y_train, scoring=scorer, cv=5).mean()
```
