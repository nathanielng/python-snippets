#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import numpy as np


EDGE_KERNELS = {
    'rectangle': cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
    'ellipse': cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
    'cross': cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
}


def display_image(img, figsize=(10, 7), interpolation='none', filename=None):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.imshow(img, cmap='gray', interpolation=interpolation)
    ax.set_xticks([])
    ax.set_yticks([])

    if filename:
        plt.savefig(filename)


def display_image_1D(image_dict, orientation, figsize=(10, 7), filename=None):
    n = len(image_dict)
    if orientation == 'horizontal':
        fig, axs = plt.subplots(1, n, figsize=figsize)
    elif orientation == 'vertical':
        fig, axs = plt.subplots(n, 1, figsize=figsize)

    for i, (title, image) in enumerate(image_dict.items()):
        axs[i].imshow(image, cmap='gray', interpolation='none')
        axs[i].set_xticks([])
        axs[i].set_yticks([])
        axs[i].set_title(title)
    
    if filename:
        plt.savefig(filename)


def display_image_2D(image_dict, rows, cols, figsize=(10, 7), filename=None):
    fig, axs = plt.subplots(rows, cols, figsize=figsize)
    row, col = 0, 0
    for title, image in image_dict.items():
        axs[row][col].imshow(image, cmap='gray', interpolation='none')
        axs[row][col].set_xticks([])
        axs[row][col].set_yticks([])
        axs[row][col].set_title(title)
        col += 1
        if col == cols:
            row += 1
            col = 0
        if row*cols + col > len(image_dict):
            print('Not enough rows & columns')
            print(f'n = {len(image_dict)} > rows={rows} x cols={cols}')

    if filename:
        plt.savefig(filename)


def calculate_histograms(image_dict, method='calchist', bincount=256, figsize=(7, 5)):
    hist_dict = {}
    for title, image in image_dict.items():
        if method == 'calchist':
            # channels = [0] for grayscale images
            # histSize is the BIN count (set to 256 for full histogram)
            hist = cv2.calcHist(images=[image], channels=[0],
                                mask=None,
                                histSize=[bincount],
                                ranges=[0, 256])
        else:
            hist, bins = np.histogram(image.ravel(), 256, [0, 256])
        hist_dict[title] = hist
    return hist_dict


def show_histogram(img, bincount=256, figsize=(7, 5)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.hist(img.ravel(), bincount, [0, 256])


def display_image_n_hist(image_dict, figsize=(10, 7), filename=None):
    n = len(image_dict)
    fig, axs = plt.subplots(n, 2, figsize=figsize)

    for row, (title, image) in enumerate(image_dict.items()):
        axs[row][0].imshow(image, cmap='gray', interpolation='none')
        axs[row][0].set_xticks([])
        axs[row][0].set_yticks([])
        axs[row][0].set_title(title)
        axs[row][1].hist(image.ravel(), 256, [0, 256])

    if filename:
        plt.savefig(filename)


def denoise(img, method='blur', **kwargs):
    if method == 'blur':
        # Example kwargs: ksize=(5, 5)
        img_denoised = cv2.blur(img, **kwargs)
    elif method == 'gaussian':
        # Example kwargs: ksize=(5, 5), sigmaX=5
        img_denoised = cv2.GaussianBlur(img, **kwargs)
    elif method == 'median':
        # Example kwargs: ksize=5 (has to be odd)
        img_denoised = cv2.medianBlur(img, **kwargs)
    elif method == 'fastNlMeans':
        # Non-local Means Denoising algorithm
        img_denoised = cv2.fastNlMeansDenoising(img, **kwargs)
    elif method == 'bilateral':
        # Example kwargs: d=9, sigmaColor=75, sigmaSpace=75
        img_denoised = cv2.bilateralFilter(img, 9, 75, 75)
    return img_denoised


def combine_sobel(sobelx, sobely):
    return cv2.addWeighted(cv2.convertScaleAbs(sobelx), 0.5, cv2.convertScaleAbs(sobely), 0.5, 0)


def clip_sobel(sobelx, sobely):
    return np.clip(np.abs(sobelx) + np.abs(sobely), a_min=0, a_max=255)


def edge_detect(img, method):
    if method == 'canny':
        edges = cv2.Canny(img, 40, 100, 3)
    elif method == 'sobel16':
        sobelx = cv2.Sobel(img, cv2.CV_16S, 1, 0, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        sobely = cv2.Sobel(img, cv2.CV_16S, 0, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    elif method == 'sobel':
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    else:
        print(f'Invalid method = {method}')
        quit()

    if method in ['sobel', 'sobel16']:
        edges = np.abs(sobelx) + np.abs(sobely)
        print(f"New edges: range=({edges.min()}, {edges.max()})")
        edges_scaled = (edges*255/edges.max()).astype(np.uint8)
        return edges_scaled
    return edges


def threshold_image(img, method='adaptive_gaussian'):
    if method == 'adaptive_gaussian':
        img_t = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    else:
        thresh, img_t = cv2.threshold(
            img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return img_t


def save_images(image_dict):
    """
    Save all images, except the original image
    """
    filtered_dict = image_dict.copy()
    filtered_dict.pop('Original', None)
    for label, image in filtered_dict.items():
        filename = f'{label}.png'
        cv2.imwrite(filename, image)
        print(f"Saved: '{filename}'")


def edge_detect_multi(image_dict, method):
    new_img_dict = {}
    method_str = method.title()
    for label, img in image_dict.items():
        new_label = f'{method_str} on {label}'
        new_img_dict[new_label] = edge_detect(
            image_dict[label],
            method=method
            )
    return new_img_dict


def threshold_multi(image_dict, method):
    new_img_dict = {}
    method_str = method.title()
    for label, img in image_dict.items():
        new_label = f'{method_str} on {label}'
        new_img_dict[new_label] = threshold_image(
            image_dict[label],
            method=method
        )
    return new_img_dict
