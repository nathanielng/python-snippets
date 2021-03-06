# Remote

This folder deals with remote servers (AWS / GCP / Azure),
remote services (Google Drive / Sheets), and
remote computation (Google Colab)

## 1. Remote servers

### 1.1 Remote file copy

#### Option 1

```bash
rsync -avz -e "ssh -i ~/.ssh/id_ed25519" $LOCAL_FILES $USERID@$HOSTNAME:$REMOTE_FOLDER
```

#### Option 2

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

### 1.2 Ping

To ping a remote server, use (remove the `-c3` option to ping an unlimited number of times):

```bash
ping -c3 hostname
```

Note that inbound ICMP traffic should be enabled.  For AWS EC2 instances,
the security groups should be [configured appropriately](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html#sg-rules-ping).

### 1.3 SSH and Port Forwarding

SSH to remote server (that has been set up in `~/.ssh/config`)

```bash
ssh my_remote_aws_instance
ssh -X my_remote_aws_instance  # with X11 forwarding
ssh -Y my_remote_aws_instance  # with trusted X11 forwarding
```

SSH with port forwarding

```bash
ssh -L local_port:ip_addr:remote_port hostname
ssh -L 8080:127.0.0.1:8080 my_remote_aws_instance
ssh -N -L 8080:127.0.0.1:8080 my_remote_aws_instance  # do not execute remote commands
```

## 2. Google Colaboratory

### 2.1 Introduction

The **Welcome to Google Colaboratory** notebook may be accessed at
[https://colab.research.google.com/notebooks/intro.ipynb](https://colab.research.google.com/notebooks/intro.ipynb).
A guide to transferring data into a Google Colab notebook is provided at
[https://colab.research.google.com/notebooks/io.ipynb](https://colab.research.google.com/notebooks/io.ipynb).
It is also possible to use [`gdown`](https://pypi.org/project/gdown/) `--id google_drive_file_id` to
transfer a file from Google Drive into a Colab notebook.

### 2.2 Opening Github Jupyter notebooks on Colab

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
