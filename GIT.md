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

## 3. Notes

Replace `{userid}` with your user id and replace `{reponame}`
with the name of your Github repository.  If your repository is not
hosted on Github, replace `github.com` with the name of your server.