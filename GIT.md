# Git Usage Guide

## 1. Repository Creation

### 1.1 New Local+Remote Repository

Instructions for creating a new *local* repository,
and pushing it to Github, thereby also creating a
new *remote* repository.

#### 1.1.1 First Commit

Set your name and email. A
[privacy email](https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/setting-your-commit-email-address)
of the form `userid@users.noreply.github.com` is available at
[https://github.com/settings/emails](https://github.com/settings/emails).

```bash
git init
git config --local user.name "Firstname Lastname"
git config --local user.email "userid@hostname"
git config --global core.editor "vim"  # Optional. replace vim with nano, ..., depending on the preferred editor for commits

git add new_file
git commit -m "First commit"
git tag v0.1
```

#### 1.1.2 First Branch

```bash
git checkout -b develop
git add new_file
git commit -m "Second commit"
git tag v0.2
```

#### 1.1.3 First Push (creates new remote repository)

```bash
git remote add origin https://github.com/{userid}/{reponame}.git
git push origin --all
git push origin --tags
```

### 1.2 Existing Local Repository, New Remote Repository

Instructions for creating a new *remote* repository,
from the contents of an existing *local* repository.

#### 1.2.1 Add remote to an existing local git repository

First create an empty repository on Github,
then add the remote address to your existing local git repository.

```bash
git remote add {remote_name} git@github.com:{userid}/{reponame}.git
```

For *remote_name*, a typical choice is `origin` (this will not work
if the git repo already has a remote named `origin`, in which case
another choice will be necessary).


#### 1.2.2 Pushing the local git repository to Github

```bash
git push -u {remote_name} master
```

## 2. Repository Management

### 2.1 Inspecting a repository

```bash
git status       # View repository status
git log          # View git history
git branch -avv  # View local & remote branches
git remote -v    # View remote URLs
```

### 2.2 Keeping a fork synchronised with an upstream repository

```bash
cd path/to/{reponame}
git remote add upstream git@github.com:{userid}/{reponame}.git
git checkout master
git fetch upstream
git merge upstream/master
git push origin master
```

### 2.3 Changing a repository URL

```bash
git remote set-url origin git@github.com:{userid}/{reponame}.git
```

## 3. Notes

Replace `{userid}` with your user id and replace `{reponame}`
with the name of your Github repository.  If the repository is not
hosted on Github, replace `github.com` with the name of the server.
