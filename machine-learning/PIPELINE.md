# Machine Learning Process

## 1. Steps of a machine learning process

### 1.1 Data preparation & transformations

1. Data ingestion
2. Data quality checks: duplicate rows, missing values, collinearity / highly correlated variables, outliers, checks for insufficient data, ...
3. Data processing: categorical data - one-hot encoding (on features), ova vs ovo (on target). date conversions. numerical conversions. unicode handling.
4. Feature engineering & target engineering
5. Data transformations: standard scaler, min-max scaler, quantile transforms, etc.
6. Dimension reduction, if required
7. Corrections for data imbalance, if required

### 1.2 Model & optimization choices

1. Choice of target variable(s)
2. Choice of evaluation metric
3. Choice of machine learning model(s)

### 1.3 Training

1. Choice of splits & cross-validation scheme
2. Model Training
3. Hyperparameter Tuning
4. Model Evaluation based on selected metric

### 1.4 Final steps

1. Deployment of model
2. Ingestion of new training data & rebuilding the model
3. Maintaining the model
