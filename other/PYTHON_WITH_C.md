# Python with C

## 1. Creating a static library

```bash
gcc -c file1.c file2.c
ar [options] libraryfile.a file1.o file2.o
```

## 2. Creating a dynamically linked library

```bash
gcc -fPIC file1.c file2.c -o libraryfile.so
```

**Flags**

- `-fPIC`: generate position independent code

