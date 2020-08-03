# Math

## 1. Integration

### 1.1 Quadrature

- [`scipy.integrate()`](https://docs.scipy.org/doc/scipy/reference/integrate.html) - `quad`, `fixed_quad`, `quadrature`

**Example Code**

```python
import numpy as np
from functools import partial
from scipy.integrate import fixed_quad, quad, quadrature, romberg

def my_func(x, a):
    return np.sin(x*a)

my_func2 = partial(my_func, 0.5)


%time area1, err1 = fixed_quad(my_func2, a=0, b=np.pi)
assert np.allclose([area1], [2])
print(f'Area under curve (fixed_quad) = {area1} (Error = {err1})')

%time area2, err2 = quadrature(my_func2, a=0, b=np.pi)
print(f'Area under curve (quadrature) = {area2} (Error = {err2})')
assert np.allclose([area2], [2])

%time area3, err3 = quad(my_func2, a=0, b=np.pi)
print(f'Area under curve (quad) = {area2} (Error = {err3})')
assert np.allclose([area3], [2])
```

**Output**

```
CPU times: user 0 ns, sys: 698 µs, total: 698 µs
Wall time: 705 µs
Area under curve (fixed_quad) = 2.0000000000791305 (Error = None)
CPU times: user 2.18 ms, sys: 36 µs, total: 2.22 ms
Wall time: 1.88 ms
Area under curve (quadrature) = 1.999999999999907 (Error = 7.922351663580685e-11)
CPU times: user 78 µs, sys: 16 µs, total: 94 µs
Wall time: 97.3 µs
Area under curve (quad) = 1.999999999999907 (Error = 2.2204460492503128e-14)
```

**Check the Solution**

$$\int_0^\pi \sin(ax) = \left[-\frac{1}{a}\cos(ax)\right]_0^\pi$$
$$= -\frac{1}{a}\left[\cos(\pi a) - 1\right]$$
$$= \frac{1}{a}\left[1 - \cos(\pi a)\right]$$

$$\int_0^\pi \sin\left(\frac{1}{2}x\right) = 2\left[1 - \cos\left(\frac{\pi}{2}\right)\right] = 2$$
