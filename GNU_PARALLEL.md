# Using GNU Parallel

## Preparation

Create a file, `command_file.sh` containing a list of commands, such as the following

```bash
./command arg1 arg2
./command arg3 arg4
.
.
.
./command arg9 arg10
```

## Job submission

Invoke GNU Parallel as follows. Replace `$JOBS` with the number of processors
on the server to be assigned to the task. For example, set `JOBS=14` to allocate
14 cores out of 16 on a 16-core machine, for running the task.

```bash
export JOBS=16
while IFS= read -r line; do echo "$line"; done < command_file.sh | parallel --jobs $JOBS
```

