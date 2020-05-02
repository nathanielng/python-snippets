# PostgreSQL

## 1. Setup

### 1.1 Installation

View all processes owned by the user `postgres` and
check that the process is listening

```
ps -f -u postgres
netstat -nap | grep postgres
```

Check for `psql`:

```bash
which psql
```

### 1.2 User Setup

```bash
psql
```

From the PostgreSQL prompt

```
CREATE USER userid WITH PASSWORD 'my_postgresql_password';
```

### 1.3 Database Creation

From the command line

```bash
createdb -O db_owner database_name
```

From the PostgreSQL prompt

```
CREATE DATABASE database_name OWNER db_owner ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
GRANT ALL PRIVILEGES ON DATABASE database_name to db_owner;
```

**Note**: replace `db_owner` with the user id of the owner of the database.
replace `database_name` with the name of the database.

## 2. Usage

### 2.1 Connecting to a database

```bash
psql -U userid -d database_name
psql -d database_name -U userid -h localhost -W
psql -d database_name -U userid -h 127.0.0.1 -W
psql -d postgresql://userid:password@hostname:5432/database_name
psql -d "user=userid host=localhost port=5432 dbname=database_name"
PGPASSWORD=password psql -h hostname -d database_name -U user_id
```

**Note**: the `-W` option is to force the prompt for the password

