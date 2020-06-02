# Least Squares Optimization

## 1. Define the search space

```python
N = 1000
a_array = np.random.uniform(low=a_min, high=a_max, size=N)
b_array = np.random.uniform(low=b_min, high=b_max, size=N)
c_array = np.random.uniform(low=c_min, high=c_max, size=N)
```

## 2. Define the function

```python
def fn_to_optimize(params, fixed_param1, fixed_param2):
    a, b, c = params
    return fn(a, b, c, fixed_param1, fixed_param2)
```

## 3. Define a subroutine to store results in a dataframe

```python
def result2df(x0, r):
    if r is None:
        a, b, c = np.nan, np.nan, np.nan
        cost = np.nan
        nfev = -1
        status = -1
    else:
        a, b, c = r.x
        cost = r.cost
        nfev = r.nfev
        status = r.status

    df = pd.DataFrame({
        'a_guess': x0[0],
        'b_guess': x0[1],
        'c_guess': x0[2],
        'a': tau,
        'b': t0,
        'c': theta,
        'nfev': nfev,
        'Error': cost,
        'Status': status
    }, index=[0])
    return df
```

## 4. Perform function evaluations over the search space

Load previous results (if they exist)

```python
if os.path.isfile(results_file):
        df_r = pd.read_csv(results_file)
    else:
        df_r = pd.DataFrame()
```

Perform function evaluations over the search space

```python
for a, b, c in zip(a_array, b_array, c_array):
    params = (a, b, c)
    print(f'a = {a:.3f}, b = {b:.3f}, c = {theta:.3f}', end='')
    try:
        r = least_squares(fn_to_optimize, x0=params, args=(
            fixed_param1, fixed_param2), max_nfev=200*3, method='trf')
        a, b, c = r.x
        print(f' Final: ({a:.3f}, {b:.3f}, {c:.3f})', end='')
        print(f' (Cost = {r.cost} after {r.nfev} evals. Status: {r.status})')
    except Exception as e:
        r = None
        print(' [Exception: {e}]')
    finally:
        df_r = df_r.append(result2df(params, r))

df_r = df_r.reset_index(drop=True)
```

## 5. Summarize the results

Print the best results so far

```python
df_best=df_r.dropna(axis=0, how='any', subset=['Error']).sort_values(
    'Error', ascending = True).head(20)
print(df_best)
```

Save the results file

```python
df_r.to_csv(results_file)
```
