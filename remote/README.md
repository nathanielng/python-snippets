# Remote

This folder deals with remote servers (AWS / GCP / Azure),
remote services (Google Drive / Sheets), and
remote computation (Google Colab)

## 1. Remote file copy

### Option 1

```bash
rsync -avz -e "ssh -i ~/.ssh/id_ed25519" $LOCAL_FILES $USERID@$HOSTNAME:$REMOTE_FOLDER
```

### Option 2

Edit `~/.ssh/config`, specifying the hostname, userid, and identity file.
For example, for an AWS EC2 instance, this might take the form:

```
Host my_remote_aws_instance
    Hostname ec2-xx-xx-xx-xx.aws_region.compute.amazonaws.com
    User ec2-user
    IdentityFile ~/.ssh/id_ed25519
```

```bash
rsync -avz $LOCALFILES my_remote_aws_instance:$REMOTE_FOLDER
```

## 2. Google Colaboratory

### 2.1 Opening Github Jupyter notebooks on Colab

For a Jupyter notebook, in a Github repository at the following location:

```
https://github.com/username/repo/blob/master/my_notebook.ipynb
```

Open the notebook in Colab using

```
http://colab.research.google.com/github/username/repo/blob/master/my_notebook.ipynb
```

It is also possible to browse around in Colab using

```
http://colab.research.google.com/github                # General Github browser
http://colab.research.google.com/github/username       # Browse repositories of a user
http://colab.research.google.com/github/username/repo  # Browse a specific repo
```

Create an **Open in Colab** badge for a notebook using

```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/username/repo/blob/master/my_notebook.ipynb)
```

Source: https://colab.research.google.com/github/googlecolab/colabtools/blob/master/notebooks/colab-github-demo.ipynb
