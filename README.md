# Petal 🌸

**A small, Python-flavored scripting language that grows with you.**

Petal is a minimal, elegant programming language designed to be easy to learn while remaining powerful enough for real programs. It compiles to a tree-walking interpreter implemented in a single, readable Python file (~1,200 lines).

## Features

- **Simple Syntax**: Python-like syntax that feels natural and readable
- **Dynamic Typing**: Variables don't need type declarations
- **First-Class Functions**: Functions are values; closures work as expected
- **Collections**: Lists and dictionaries with built-in methods
- **Control Flow**: `if`/`elif`/`else`, `while`, `for`, `break`, `continue`
- **String Interpolation**: F-strings for easy string formatting
- **Browser Playground**: Run Petal directly in your browser via Pyodide (WebAssembly)
- **Single-File Implementation**: The entire interpreter fits in one readable file

## Quick Start

### Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/petal.git
cd petal
```

### Running Petal

**From the terminal:**
```bash
# Run a Petal script
python3 petal.py examples/hello.petal

# Start the interactive REPL
python3 petal.py
```

**In the browser:**
Open `playground.html` directly in your browser, or host it anywhere. Everything runs client-side using Pyodide—nothing you write is sent anywhere.

## Language Reference

### Hello World

```petal
name = "world"
print(f"Hello, {name}!")
```

### Variables & Types

```petal
x = 10              # int
pi = 3.14           # float
name = "Petal"      # str
ok = True           # bool
nothing = None      # null value
```

Petal is dynamically typed. Falsy values: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`. Everything else is truthy.

### Operators

```petal
# Arithmetic
+  -  *  /  //  %  **        # // is floor division, ** is power

# Comparison
== != < > <= >=

# Logical (short-circuiting)
and  or  not

# Membership
in  not in

# Compound assignment
+= -= *= /= %=
```

### Strings

```petal
"double or 'single' quotes both work"
f"embed {expressions} directly, like {1 + 2}"
```

Strings are single-line only. Use escape sequences: `\n`, `\t`, `\\`, `\"`, `\'`.

### Collections

**Lists:**
```petal
nums = [1, 2, 3]
nums.append(4)
nums[0]              # 1
nums[1:3]            # [2, 3]
```

**Dictionaries:**
```petal
person = {"name": "Abhijeet", "role": "builder"}
person["role"]
for key in person:
    print(key, person[key])
```

**Built-in methods:**
- List: `append`, `pop`, `insert`, `remove`, `index`, `count`, `reverse`, `sort`, `clear`
- String: `upper`, `lower`, `strip`, `split`, `join`, `replace`, `startswith`, `endswith`, `find`
- Dict: `keys`, `values`, `items`, `get`, `pop`

### Control Flow

```petal
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

```petal
def add(a, b):
    return a + b

def greet(name):
    print(f"hi {name}")   # implicit None return

# Closures capture their defining scope
def make_adder(x):
    def adder(y):
        return x + y
    return adder

add5 = make_adder(5)
print(add5(10))  # 15
```

### Built-in Functions

```petal
print(...)      len(x)        range(a, b, step)
str(x)          int(x)        float(x)      bool(x)
type(x)         abs(x)        min(...)      max(...)
sum(x)          sorted(x)     round(x, n)   input(prompt)
```

## Examples

### FizzBuzz

```petal
for i in range(1, 16):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

### Fibonacci

```petal
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

for i in range(10):
    print(fib(i))
```

### Working with Data Structures

```petal
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits)
print(fruits[1:3])
print("banana" in fruits)

person = {"name": "Abhijeet", "role": "builder"}
person["projects"] = ["Petal", "ToolXHub"]
for key in person:
    print(key, "->", person[key])
```

See more examples in the `examples/` directory.

## What's Deliberately Left Out

To keep the implementation small and readable, Petal doesn't have:
- Classes and objects
- Exception handling (`try`/`except`)
- Multi-line strings
- `global`/`nonlocal` keywords
- Default/keyword arguments
- `*args` and `**kwargs`
- List/dict comprehensions
- Module system

These are reasonable next steps if you want to extend Petal—the lexer, parser, and interpreter are organized so each piece is easy to find and modify in `petal.py`.

## Architecture

The entire language implementation lives in `petal.py` (~1,200 lines):

1. **Lexer** (lines ~65–196): Tokenizes source code, handles indentation
2. **Parser** (lines ~340–688): Builds an abstract syntax tree (AST)
3. **Interpreter** (lines ~732–1172): Tree-walking interpreter with environment-based scoping
4. **CLI/REPL** (lines ~1100+): Command-line interface and interactive REPL

## Browser Playground

The `playground.html` file provides an in-browser IDE powered by Pyodide (Python compiled to WebAssembly). Features:

- Live code editing with Python-aware indentation
- Pre-loaded example programs
- Real-time output display
- Syntax error reporting
- No server required—everything runs client-side

## Contributing

Contributions are welcome! Here are some ways you can help:

- **Report bugs**: Open an issue with a minimal reproducible example
- **Add features**: Extend the language with new syntax or built-ins
- **Improve documentation**: Clarify examples or add tutorials
- **Optimize performance**: Profile and improve the interpreter
- **Add tests**: Expand the test suite

## Development

### Running Tests

```bash
python3 -m pytest tests/
```

### Code Style

- Use 4-space indentation
- Keep functions focused and readable
- Add docstrings to complex logic
- Follow PEP 8 conventions

## License

Petal is released under the **MIT License**. See `LICENSE` for details.

## Inspiration

Petal draws inspiration from:
- **Python**: Clean syntax, dynamic typing, readability
- **Lua**: Minimal, embeddable, single-file implementation
- **Scheme**: Closures, first-class functions, elegant semantics

## Roadmap

Potential future enhancements:
- [ ] Module system (`import`, `from`)
- [ ] Exception handling (`try`/`except`/`finally`)
- [ ] Classes and objects
- [ ] Decorators
- [ ] Async/await
- [ ] Standard library expansion
- [ ] Performance optimizations (bytecode compilation, JIT)

## FAQ

**Q: Why create another programming language?**
A: Petal is designed as both a learning tool and a minimal, embeddable scripting language. It's small enough to understand completely, yet capable enough to solve real problems.

**Q: Can I use Petal in production?**
A: Petal is suitable for scripting, configuration, and educational purposes. For performance-critical applications, consider languages like Python, Lua, or Go.

**Q: How do I extend Petal?**
A: The implementation is intentionally readable. You can add new operators, built-in functions, or language features by modifying `petal.py`. See the "What's Deliberately Left Out" section for ideas.

**Q: Can Petal run in the browser?**
A: Yes! The `playground.html` file runs Petal in the browser via Pyodide. You can also embed the Petal interpreter in any Python environment.

## File Structure

```
petal/
├── README.md              # This file
├── LICENSE                # MIT License
├── petal.py              # Complete language implementation
├── playground.html       # Browser-based IDE
├── examples/             # Example programs
│   ├── hello.petal
│   ├── fizzbuzz.petal
│   ├── fibonacci.petal
│   ├── data_structures.petal
│   └── edge_cases.petal
├── tests/                # Test suite
├── docs/                 # Additional documentation
└── .gitignore
```

## Contact & Community

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Share ideas and ask questions
- **Email**: [your-email@example.com]

---

**Made with 🌸 by the Petal community.**

*Petal is open source and welcomes contributions from developers of all skill levels.*
