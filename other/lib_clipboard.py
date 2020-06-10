#!/usr/bin/env python

# Dependencies:
# pip install pandas Pillow richxerox


def grab_screen_image(img_file: str='screen.png'):
    from PIL import ImageGrab, Image
    screen = ImageGrab.grab()
    screen.save(img_file)


def grab_clipboard_image(backend: str='PIL'):
    if backend == 'PIL':
        from PIL import ImageGrab, Image
        clip = ImageGrab.grabclipboard()
        clip.save('clip.png')


def grab_clipboard_text(backend: str='pandas'):
    if backend == 'pandas':
        from pandas.io.clipboard import clipboard_get
        text = clipboard_get()
    elif backend == 'richxerox':
        pass


if __name__ == "__main__":
    pass
