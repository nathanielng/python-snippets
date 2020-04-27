# Computer Vision

## 1. PIL / Pillow

### 1.1 Reading an image

```python
import PIL
img = PIL.Image.open('imagefile.png')
```

### 1.2 Displaying an image

In a Jupyter notebook:

```python
img
```


## 2. Scikit Image

### 2.1 Installation

```bash
pip install scikit-image
```

### 2.2 Reading an image

```python
import skimage.io as io
img = io.imread('imagefile.png')
```

### 2.3 Displaying an image

```python
io.imshow(img)
```


## 3. OpenCV

### 3.1 Reading an image

```python
import cv2
color_image = cv2.imread('color_image.png')  # or
color_image = cv2.imread('color_image.png', cv2.IMREAD_COLOR)             # 3D matrix
grayscale_image = cv2.imread('grayscale_image.png', cv2.IMREAD_GRAYSCALE) # 2D matrix
```

### 3.2 Displaying an image

```python
plt.imshow(grayscale_image, cmap='gray', interpolation='none');
```


## 4. Sample Images

```python
import scipy.misc
ascent = scipy.misc.ascent()
face = scipy.misc.face()
```
