## Bash

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
