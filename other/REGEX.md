# Regular Expressions in Python

## 1. Module

```python
import re
```

### 1.1 Special Characters

#### 1.1.1 Metacharacters in Python's Regex Implementation

```
. ^ $ * + ? { } [ ] \ | ( )
```

Character | Description             | Escape
----------|-------------------------|------
 `[]`     | encloses characters that form a "character class"
 `?`      | match 0 or 1 repetitions
 `*`      | match 0 or more repetitions (greedy)
 `+`      | match 1 or more repetitions (greedy)
 `{a,b}`  | match between $a$ and $b$ repetitions, inclusive
 `^`      | matches the beginning of a string; when inside a `[]`, it matches characters **not** inside the class | `\^`
 `$`      | match the end of a line | `\$` or `[$]`
 `|`      | `or` operator | `\|` or `[|]`

(*) greedy: it will match as many characters as possible
(it will stop only if adding the next character will cause the match to fail)

### 1.1.2 Escape Codes

Code | Matches
-----|-------------------------
`\d` | digit
`\D` | non-digit
`\s` | whitespace
`\S` | non-whitespace
`\w` | alphanumeric
`\W` | non-alphanumeric

### 1.1.3 Flags

Abbrev | Full Flag
-------|-----------------
`re.A` | `re.ASCII`
`re.I` | `re.IGNORECASE`
`re.L` | `re.LOCALE`
`re.M` | `re.MULTILINE`
`re.S` | `re.DOTALL`
`re.X` | `re.VERBOSE`
