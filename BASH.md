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
