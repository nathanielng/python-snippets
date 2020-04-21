# f-strings in Python

## 1. Alignment & Fills

```
s = 'abc'
x = 123
y = 123456789
z = 0.01234567
```

 Justify | f-string     | Output
---------|--------------|---------
Default  | `f'{s:5}'`   | `abc  `
Left     | `f'{s:<5}'`  | `abc  `
Center   | `f'{s:^5}'`  | ` abc `
Right    | `f'{s:>5}'`  | `  abc`

 Fill    | f-string     | Output
---------|--------------|---------
Left     | `f'{s:#<5}'` | `abc##`
Center   | `f'{s:#^5}'` | `#abc#`
Right    | `f'{s:#>5}'` | `##abc`
Left     | `f'{x:0<5}'` | `12300`
Center   | `f'{x:0^5}'` | `01230`
Right    | `f'{x:05}'`  | `00123`

## 2. Integers

| Category    | f-string     | Output        |
|-------------|--------------|---------------|
| Integer     | `f'{x:d}'`   | `123`         |
| Commas      | `f'{y:,d}'`  | `123,456,789` |
| Postive     | `f'{x:+d}'`  | `+123`        |
| Negative    | `f'{-x:-d}'` | `-123`        |
| Binary      | `f'{x:b}'`   | `1111011`     |
|             | `f'{x:#b}'`  | `0b1111011`   |
| Octal       | `f'{x:o}'`   | `173`         |
|             | `f'{x:#o}'`  | `0o173`       |
| Hexadecimal | `f'{x:x}'`   | `7b`          |
|             | `f'{x:#x}'`  | `0x7b`        |
|             | `f'{x:X}'`   | `7B`          |
| ASCII       | `f'{x:c}'`   | `{`           |

## 3. Floats

| Category    | f-string     | Output         |
|-------------|--------------|----------------|
| Fixed       | `f'{z:f}'`   | `0.012346`     |
|             | `f'{z:.5f}'` | `0.01235`      |
| Exponential | `f'{z:e}'`   | `1.234567e-02` |
|             | `f'{z:.5e}'` | `1.23457e-02`  |
| Percentage  | `f'{z:0%}'`  | `1.234567%`    |
|             | `f'{z:.2%}'` | `1.23%`        |
