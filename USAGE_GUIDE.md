# Petal Language - Complete Usage Guide

## Overview

Petal is a lightweight, Python-inspired scripting language that's easy to learn and powerful enough for real applications. This guide covers everything you need to know to start using Petal effectively.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Running Petal Programs](#running-petal-programs)
3. [Language Basics](#language-basics)
4. [Data Types & Operations](#data-types--operations)
5. [Control Flow](#control-flow)
6. [Functions & Closures](#functions--closures)
7. [Working with Collections](#working-with-collections)
8. [String Operations](#string-operations)
9. [Built-in Functions](#built-in-functions)
10. [Common Patterns](#common-patterns)
11. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- Git (optional, for cloning the repository)

### Getting Started

**Option 1: Clone from GitHub**
```bash
git clone https://github.com/yourusername/petal.git
cd petal
```

**Option 2: Download Files**
- Download `petal.py` and any example files you need

### Verify Installation

```bash
python3 petal.py
```

You should see the Petal REPL prompt. Type `exit()` to quit.

---

## Running Petal Programs

### Running a Script File

Create a file named `hello.petal`:
```petal
print("Hello, Petal!")
```

Run it:
```bash
python3 petal.py hello.petal
```

### Interactive REPL

```bash
python3 petal.py
```

Then type Petal code directly:
```
>>> name = "World"
>>> print(f"Hello, {name}!")
Hello, World!
```

### Browser Playground

Open `playground.html` in your web browser for a visual IDE with:
- Code editor
- Run button
- Real-time output
- Pre-loaded examples

---

## Language Basics

### Comments

```petal
# This is a comment
x = 10  # Comments can go at the end of lines too
```

### Variables & Assignment

```petal
x = 10
y = 20
x = x + y  # Reassignment

# Multiple assignment
a, b = 1, 2  # Not supported; use separate statements
```

### Variable Naming Rules

- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive: `name` and `Name` are different
- Avoid reserved keywords: `if`, `def`, `return`, etc.

---

## Data Types & Operations

### Numbers

```petal
# Integers
x = 42
y = -10

# Floats
pi = 3.14159
e = 2.71828

# Arithmetic
a = 10 + 5      # 15
b = 10 - 5      # 5
c = 10 * 5      # 50
d = 10 / 3      # 3.333...
e = 10 // 3     # 3 (floor division)
f = 10 % 3      # 1 (modulo)
g = 2 ** 8      # 256 (exponentiation)
```

### Booleans

```petal
is_active = True
is_deleted = False

# Boolean operations
result = True and False  # False
result = True or False   # True
result = not True        # False
```

### None (Null)

```petal
nothing = None
if nothing == None:
    print("It's nothing!")
```

### Type Conversion

```petal
x = int("42")       # 42
y = float("3.14")   # 3.14
z = str(100)        # "100"
b = bool(1)         # True
```

### Checking Types

```petal
x = 42
print(type(x))      # int

y = "hello"
print(type(y))      # str
```

---

## Control Flow

### If Statements

```petal
age = 18

if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
```

### While Loops

```petal
count = 0
while count < 5:
    print(count)
    count += 1
```

### For Loops

```petal
# Loop over a range
for i in range(5):
    print(i)        # 0, 1, 2, 3, 4

# Loop over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Loop over dictionary keys
person = {"name": "Alice", "age": 30}
for key in person:
    print(key, person[key])
```

### Break & Continue

```petal
# Break: exit loop early
for i in range(10):
    if i == 5:
        break
    print(i)        # 0, 1, 2, 3, 4

# Continue: skip to next iteration
for i in range(5):
    if i == 2:
        continue
    print(i)        # 0, 1, 3, 4
```

---

## Functions & Closures

### Defining Functions

```petal
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")      # Hello, Alice!
```

### Return Values

```petal
def add(a, b):
    return a + b

result = add(3, 5)
print(result)       # 8
```

### Functions Without Return

```petal
def say_hello():
    print("Hello!")

x = say_hello()
print(x)            # None
```

### Closures

```petal
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

times_three = make_multiplier(3)
print(times_three(10))      # 30
```

### Scope Rules

```petal
x = "global"

def test():
    x = "local"     # Creates a new local variable
    print(x)        # local

test()
print(x)            # global (unchanged)
```

---

## Working with Collections

### Lists

```petal
# Creating lists
numbers = [1, 2, 3, 4, 5]
mixed = [1, "two", 3.0, True]
empty = []

# Accessing elements
first = numbers[0]      # 1
last = numbers[-1]      # 5

# Slicing
subset = numbers[1:4]   # [2, 3, 4]
first_three = numbers[:3]   # [1, 2, 3]

# List methods
numbers.append(6)       # Add to end
numbers.pop()           # Remove from end
numbers.insert(0, 0)    # Insert at position
numbers.remove(3)       # Remove by value
index = numbers.index(2)    # Find index
count = numbers.count(1)    # Count occurrences
numbers.reverse()       # Reverse in place
numbers.sort()          # Sort in place
numbers.clear()         # Remove all elements
```

### Dictionaries

```petal
# Creating dictionaries
person = {"name": "Alice", "age": 30, "city": "NYC"}
empty = {}

# Accessing values
name = person["name"]   # Alice
age = person.get("age")     # 30
unknown = person.get("job", "Unknown")  # Unknown (default)

# Adding/updating
person["job"] = "Engineer"
person["age"] = 31

# Dictionary methods
keys = person.keys()    # ["name", "age", "city", "job"]
values = person.values()    # ["Alice", 31, "NYC", "Engineer"]
items = person.items()  # [("name", "Alice"), ("age", 31), ...]

# Removing
person.pop("job")       # Remove and return value

# Iterating
for key in person:
    print(key, person[key])
```

### Checking Membership

```petal
numbers = [1, 2, 3, 4, 5]
print(3 in numbers)     # True
print(10 in numbers)    # False

person = {"name": "Alice", "age": 30}
print("name" in person)     # True
print("job" in person)      # False
```

---

## String Operations

### Creating Strings

```petal
single = 'Hello'
double = "World"
empty = ""
```

### String Concatenation

```petal
greeting = "Hello" + " " + "World"
print(greeting)         # Hello World
```

### String Interpolation (F-strings)

```petal
name = "Alice"
age = 30
message = f"My name is {name} and I'm {age} years old"
print(message)  # My name is Alice and I'm 30 years old

# Expressions in f-strings
x = 10
y = 20
print(f"{x} + {y} = {x + y}")    # 10 + 20 = 30
```

### String Methods

```petal
text = "Hello World"

# Case conversion
upper = text.upper()        # HELLO WORLD
lower = text.lower()        # hello world

# Searching
index = text.find("World")  # 6
starts = text.startswith("Hello")   # True
ends = text.endswith("World")       # True

# Manipulation
trimmed = "  hello  ".strip()   # hello
parts = "a,b,c".split(",")     # ["a", "b", "c"]
joined = "-".join(["a", "b", "c"])     # a-b-c
replaced = text.replace("World", "Petal")  # Hello Petal
```

### String Length

```petal
text = "Hello"
length = len(text)      # 5
```

---

## Built-in Functions

### I/O

```petal
# Print output
print("Hello")
print("a", "b", "c")    # Prints with spaces: a b c

# Get input
name = input("What's your name? ")
print(f"Hello, {name}!")
```

### Type Functions

```petal
print(type(42))         # int
print(type("hello"))    # str
print(type([1, 2]))     # list
print(type({"a": 1}))   # dict
```

### Conversion Functions

```petal
print(int("42"))        # 42
print(float("3.14"))    # 3.14
print(str(100))         # "100"
print(bool(1))          # True
```

### Numeric Functions

```petal
print(abs(-10))         # 10
print(min(3, 1, 4, 1, 5))   # 1
print(max(3, 1, 4, 1, 5))   # 5
print(sum([1, 2, 3, 4]))    # 10
print(round(3.14159, 2))    # 3.14
```

### Collection Functions

```petal
print(len([1, 2, 3]))       # 3
print(len("hello"))         # 5
print(sorted([3, 1, 4, 1, 5]))  # [1, 1, 3, 4, 5]
```

### Range

```petal
# range(stop)
for i in range(5):
    print(i)            # 0, 1, 2, 3, 4

# range(start, stop)
for i in range(2, 5):
    print(i)            # 2, 3, 4

# range(start, stop, step)
for i in range(0, 10, 2):
    print(i)            # 0, 2, 4, 6, 8
```

---

## Common Patterns

### Counting

```petal
count = 0
for i in range(10):
    if i % 2 == 0:
        count += 1
print(count)            # 5
```

### Accumulating

```petal
total = 0
for i in range(1, 6):
    total += i
print(total)            # 15
```

### Building Lists

```petal
squares = []
for i in range(1, 6):
    squares.append(i * i)
print(squares)          # [1, 4, 9, 16, 25]
```

### Searching

```petal
items = [1, 2, 3, 4, 5]
target = 3
found = False
for item in items:
    if item == target:
        found = True
        break
print(found)            # True
```

### Filtering

```petal
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = []
for num in numbers:
    if num % 2 == 0:
        evens.append(num)
print(evens)            # [2, 4, 6, 8, 10]
```

---

## Troubleshooting

### Common Errors

**SyntaxError: Indentation**
```petal
# Wrong: Inconsistent indentation
if True:
  print("hello")
    print("world")

# Right: Consistent indentation
if True:
    print("hello")
    print("world")
```

**NameError: Undefined Variable**
```petal
# Wrong
print(undefined_variable)

# Right: Define the variable first
undefined_variable = "defined"
print(undefined_variable)
```

**TypeError: Wrong Type**
```petal
# Wrong
result = "5" + 3

# Right: Convert to same type
result = int("5") + 3
result = "5" + str(3)
```

**IndexError: List Index Out of Range**
```petal
# Wrong
items = [1, 2, 3]
print(items[10])

# Right: Check length first
if len(items) > 10:
    print(items[10])
```

### Debugging Tips

1. **Use print statements**: Add `print()` to see variable values
2. **Check types**: Use `type()` to verify data types
3. **Test incrementally**: Build and test small pieces
4. **Read error messages**: They usually tell you what's wrong

---

## Next Steps

- Explore the examples in the `examples/` directory
- Try the browser playground at `playground.html`
- Read the main README.md for more details
- Check CONTRIBUTING.md if you want to extend Petal

Happy coding with Petal! 🌸
