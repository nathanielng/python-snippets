# Git Usage Guide

## 1. Repository Creation

### 1.1 New Repository

#### 1.1.1 First Commit

```bash
git init
git config --local user.name "Firstname Lastname"
git config --local user.email "userid@hostname"
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

#### 1.1.3 First Push

```bash
git remote add origin https://github.com/{userid}/{reponame}.git
git push origin --all
git push origin --tags
```

## 2. Repository Maintenance

### 2.1 Keeping a fork synchronised with an upstream repository

```bash
cd path/to/{reponame}
git remote add upstream git@github.com:{userid}/{reponame}.git
git checkout master
git fetch upstream
git merge upstream/master
git push origin master
```
