# Petal 🌸

A small, Python-flavored scripting language. One file (`petal.py`) is the
whole implementation — lexer, parser, tree-walking interpreter, and a CLI/REPL —
and the same file powers `playground.html`, an in-browser playground built on
Pyodide (Python compiled to WebAssembly).

```
name = "world"
print(f"Hello, {name}!")

def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

for i in range(10):
    print(fib(i))
```

## Running it

**From the terminal:**
```
python3 petal.py your_script.petal   # run a file
python3 petal.py                     # start the REPL
```

**In the browser:** open `playground.html` directly, or host it anywhere —
it's a single self-contained file with no build step and no server.
Everything runs client-side; nothing the user types is sent anywhere.

## Language reference

### Comments
```
# this is a comment
```

### Variables & types
```
x = 10          # int
pi = 3.14       # float
name = "Abhi"   # str
ok = True       # bool
nothing = None
```
Petal is dynamically typed, same as Python. Falsy values: `None`, `False`,
`0`, `0.0`, `""`, `[]`, `{}`. Everything else is truthy.

### Operators
```
+  -  *  /  //  %  **        # arithmetic (// floor division, ** power)
== != < > <= >=               # comparison
and  or  not                  # logical (short-circuiting)
in  not in                    # membership
+= -= *= /= %=                # compound assignment
```

### Strings
```
"double or 'single' quotes both work"
f"embed {expressions} directly, like {1 + 2}"
```
Strings are single-line only — no `\n` inside a literal (use `\n` as an
escape instead).

### Collections
```
nums = [1, 2, 3]
nums.append(4)
nums[0]              # 1
nums[1:3]            # [2, 3]

person = {"name": "Abhijeet", "role": "builder"}
person["role"]
for key in person:
    print(key, person[key])
```

Built-in list methods: `append, pop, insert, remove, index, count, reverse,
sort, clear`
Built-in string methods: `upper, lower, strip, split, join, replace,
startswith, endswith, find`
Built-in dict methods: `keys, values, items, get, pop`

### Control flow
```
if score > 90:
    print("A")
elif score > 75:
    print("B")
else:
    print("C")

while count < 5:
    count += 1

for item in [1, 2, 3]:
    if item == 2:
        continue
    if item == 3:
        break
```

### Functions
```
def add(a, b):
    return a + b

def greet(name):
    print(f"hi {name}")   # implicit None return

# closures capture their defining scope
def make_adder(x):
    def adder(y):
        return x + y
    return adder
```
Assigning to a variable inside a function always creates/updates a
**local** binding, the same as plain Python without `nonlocal` — a function
can read outer variables but writing to a name always writes locally.

### Built-in functions
```
print(...)      len(x)        range(a, b, step)
str(x)          int(x)        float(x)      bool(x)
type(x)         abs(x)        min(...)      max(...)
sum(x)          sorted(x)     round(x, n)   input(prompt)
```

## What's deliberately left out

To keep the implementation small and readable, Petal doesn't have: classes,
exceptions (`try`/`except`), multi-line strings, `global`/`nonlocal`,
default/keyword arguments, `*args`, list/dict comprehensions, or modules.
All of these are reasonable next steps if you want to extend it — the
lexer/parser/interpreter are ~1,200 lines total and organized so each piece
is easy to find in `petal.py`.

## Files

| File | What it is |
|---|---|
| `petal.py` | The whole language: lexer, parser, interpreter, CLI, REPL |
| `playground.html` | Self-contained browser playground (Pyodide) |
| `examples/` | Sample `.petal` programs |
