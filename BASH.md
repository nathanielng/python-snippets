## Bash & Command Line Tools

### 1. Clipboard tricks

#### 1.1 Mac OS X

Convert clipboard rich text (or html) to plain text (Mac OS X)

```bash
pbpaste | pbcopy
```

Remove newlines in clipboard text (Mac OS X)

```bash
pbpaste | xargs | pbcopy
```

#### 1.2 Linux

```bash
sudo apt install xclip
alias pbcopy='xclip -selection clipboard'
alias pbpaste='xclip -selection clipboard'
```

### 2. Downloading files from the command line

#### 2.1 wget

To download a file:

```bash
wget [url]
```

To resume (continue) a  previous download:

```bash
wget -c [url]  # or
wget --continue [url]
```

#### 2.2 curl

To download a file:

```bash
curl -O [url]  # or
curl -L -o 'outputfile' [url]
```

To resume (continue) a previous download:

```bash
curl -L -o 'outputfile' -C [offset] [url]
curl -L -o 'outputfile' -C - [url]
```

where `-L` is to follow redirects (HTTP 3xx status code)

#### 2.3 date

```bash
date +"%Y-%M-%dT%H:%M:%SZ"
```

### 3. Networking

#### 3.1 ssh

SSH to a remote server:

```bash
ssh hostname
ssh user@hostname 
```

SSH to remote server with port forwarding:

```bash
ssh -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} user@hostname
```

Running commands on a remote server:

```bash
ssh hostname "command1; command2"
ssh hostname ls -al
ssh hostname "df -h; free -h"
ssh hostname "ps aux"
ssh hostname "netstat -natp"
ssh hostname "sudo apt update && sudo apt -y upgrade"
```

Copying files from a remote server

```bash
rsync -avz hostname:filename .
```

#### 3.2 Netstat

```bash
netstat -rn    # view route table & default gateway
```

### 4. Tools for file manipulation

#### 4.1 File viewing and slicing

```bash
head -5 file.csv           # first 5 lines of a file
sed -n '10,20p' file.csv   # lines 10-20 (inclusive) of a file
tail -5 file.csv           # last 5 lines of a file
cut -f3 -d ',' test.csv    # view 3rd column of a comma-delimited file
ls -l@ filename            # view extended attributes of file (Mac OS X)
```

#### 4.2 File diff tools

```bash
diff file1.txt file2.txt      # Standard Diff Tool
opendiff file1.txt file2.txt  # Diff with FileMerge
code -d file1.txt file2.txt   # Diff with Visual Studio Code
```

#### 4.3 File compression

```bash
zip -r file.zip foldername
zip -P 'passwd' file.zip file1.txt file2.txt
zip -rP 'passwd' file.zip folder/*
unzip -P 'passwd' file.zip
```

#### 4.4 Base64 encoding

**Encoding and decoding strings**

```bash
echo "Hello world" | base64                 # Output: SGVsbG8gd29ybGQK
echo "SGVsbG8gd29ybGQK" | base64 --decode   # Output: Hello world
```

**Encoding and decoding files**

```bash
echo "Hello world" > hello_world.txt
base64 -i hello_world.txt
base64 -i hello_world.txt -o hello_world_base64.txt

base64 -d hello_world_base64.txt
base64 -d hello_world_base64.txt -o hello_world.txt
```

Encoding and decoding using OpenSSL

```bash
openssl base64 -in hello_world.txt -out hello_world_base64.txt
openssl base64 -d -in hello_world_base64.txt -out hello_world.txt
```

### 5. Tools for Video

#### 5.1 ffmpeg

Video file conversion (to make the video viewable on Mac OS X / Ubuntu)

```bash
ffmpeg -i input_video.mp4 -qscale 0 -pix_fmt yuv420p output_video.mp4
```

Image series to video conversion
(if image sequence is `m01.png`, `m02.png`, ...)

```bash
ffmpeg -f image2 -i m%d.png -r [frame_rate] -b [bit_rate] -s [dimensions] video.avi
ffmpeg -f image2 -i m%d.png -sameq -vcodec mjpeg video.avi
ffmpeg -f image2 -i m%d.png -sameq video.mpeg
ffmpeg -f image2 -i m%d.png -sameq video.mp4
ffmpeg -f image2 -r 5 -i image-%04d.png -sameq -r 25 animation.mpeg
ffmpeg -f image2 -r 5 -i image-%04d.png -qscale 0 -r 25 -vcodec libx264 -pix_fmt yuv420p animation.mp4
ffmpeg -y -f image2 -i image%03d.png -q:v 0 -vcodec libx264 -pix_fmt yuv420p anim_loop.mp4
```

Video conversion to image series or gif file

```bash
ffmpeg -i animation.mp4 -r 10 output%05d.png
convert output*.png output.gif
```

### 6. Git Bash on Windows

#### 6.1 Bash

```bash
cd /d  # Change to D: drive
cd     # Change to /c/Users/[Windows User Name]
```

#### 6.2 Git Bash with Anaconda Python

With the default installation settings (for miniconda)

```bash
which git     # should display /mingw64/bin/git
which python  # should display /c/Users/[Windows User Name]/miniconda3/python
which pip     # should display /c/Users/[Windows User Name]/miniconda3/Scripts/pip
pip install -q jupyter
which jupyter # should display /c/Users/[Windows User Name]/miniconda3/Scripts/jupyter
jupyter notebook &
```
