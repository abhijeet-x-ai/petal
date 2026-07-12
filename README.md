# Petal

**A small, Python-flavored scripting language + full-stack web framework.**

Build fast, SEO-optimized websites with simple, readable code. No JavaScript. No complex build tools. Just Python-like syntax that compiles to pure HTML & CSS.

## Overview

Petal started as a minimal scripting language (~1,200 lines) and has grown into a full-stack framework capable of:

- **Scripting**: Variables, loops, functions, closures, and 40+ built-ins
- **Static Site Generation (SSG)**: File-based routing, components, layouts
- **Server-Side Rendering (SSR)**: Dynamic page execution at request time
- **API Routes**: RESTful endpoints in `.petal` files
- **Full-Stack Serving**: Dev server with hot-reload, production server
- **Automatic SEO**: Meta tags, Open Graph, Twitter Cards, JSON-LD, sitemap, robots.txt
- **Browser Playground**: Run Petal directly in your browser via Pyodide

## Features

| Feature | Traditional Frameworks | Petal |
|---|---|---|
| **Setup** | Node.js, npm, config files | Just Python |
| **Syntax** | JSX, JavaScript, TypeScript | Python-like — anyone can read it |
| **SEO** | Manual meta tags | Automatic on every page |
| **Output** | JavaScript bundles | Pure HTML & CSS — zero JS |
| **Loading** | Depends on bundle size | Instant — pre-built static files |
| **Learning curve** | Days to weeks | Minutes |

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/abhijeet-x-ai/petal.git
cd petal
```

No package manager needed — Petal runs with Python 3 alone.

### 2. Create a New Website

```bash
python petal_cli.py new my-website
```

### 3. Start Developing

```bash
cd my-website
python ../petal_cli.py dev
```

Your site is live at `http://localhost:3000` with auto-rebuild on file changes.

### 4. Build for Production

```bash
python ../petal_cli.py build
```

Output goes to `dist/` — pure static HTML, ready for any hosting (Netlify, Vercel, GitHub Pages, any CDN).

### 5. Start Production Server

```bash
python ../petal_cli.py start
```

## CLI Commands

| Command | Description |
|---|---|
| `python petal_cli.py new <name>` | Create a new Petal website |
| `python petal_cli.py dev` | Start dev server (port 3000) |
| `python petal_cli.py build` | Build static HTML to `dist/` |
| `python petal_cli.py preview` | Preview the production build |
| `python petal_cli.py start` | Start production full-stack server |
| `python petal_cli.py run <file.petal>` | Run a Petal script |
| `python petal_cli.py --version` | Show version |

## Language Reference

### Variables & Types

```petal
x = 10              # int
pi = 3.14           # float
name = "Abhi"       # str
ok = True           # bool
nothing = None      # null value
```

Petal is dynamically typed. Falsy values: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`. Everything else is truthy.

### Strings

```petal
"double or 'single' quotes both work"
f"embed {expressions} directly, like {1 + 2}"

# Multi-line strings
bio = """
This is a multi-line
string in Petal.
"""
```

### Collections

```petal
nums = [1, 2, 3]
nums.append(4)
nums[0]              # 1
nums[1:3]            # [2, 3]

person = {"name": "Abhijeet", "role": "builder"}
person["role"]       # "builder"
person.name          # "Abhijeet" (dot-access!)
```

### Control Flow

```petal
if score > 90:
    print("A")
elif score > 75:
    print("B")
else:
    print("C")

for item in [1, 2, 3]:
    print(item)

while count < 5:
    count += 1
```

### Functions

```petal
def add(a, b):
    return a + b

# Default arguments
def greet(name="world"):
    print(f"Hello, {name}!")

greet()        # Hello, world!
greet("Abhi")  # Hello, Abhi!

# Closures capture their defining scope
def make_adder(x):
    def adder(y):
        return x + y
    return adder

add5 = make_adder(5)
print(add5(10))  # 15
```

### Operators

```petal
+  -  *  /  //  %  **        # arithmetic
== != < > <= >=               # comparison
and  or  not                  # logical
in  not in                    # membership
+= -= *= /= %=               # compound assignment
"ha" * 3                      # "hahaha" (string repeat)
```

### Built-in Functions

```petal
print(...)      len(x)          range(a, b, step)
str(x)          int(x)          float(x)
bool(x)         type(x)         abs(x)
min(...)        max(...)        sum(x)
sorted(x)       round(x, n)     input(prompt)
enumerate(x)    zip(a, b)       isinstance(x, "int")
map(fn, list)   filter(fn, list)
reversed(x)     any(x)          all(x)
```

### Built-in Methods

**Lists:** `append`, `pop`, `insert`, `remove`, `index`, `count`, `reverse`, `sort`, `clear`

**Strings:** `upper`, `lower`, `strip`, `lstrip`, `rstrip`, `split`, `join`, `replace`, `startswith`, `endswith`, `find`, `capitalize`, `title`, `count`, `center`, `zfill`, `isdigit`, `isalpha`, `isalnum`

**Dicts:** `keys`, `values`, `items`, `get`, `pop`

## Web Framework Reference

### Page Anatomy

Every `.petal` page has three sections:

```
---
# Frontmatter: server-side Petal code
title = "About Us"
description = "Learn about our team"
---

<!-- Template: HTML with {expressions} -->
<h1>{title}</h1>
<p>{description}</p>

<style>
/* Scoped styles for this page */
h1 { color: navy; }
</style>
```

### Template Syntax

```html
<!-- Output a variable -->
<h1>{title}</h1>

<!-- Loop -->
{for item in items}
    <p>{item.name}</p>
{endfor}

<!-- Conditional -->
{if show_banner}
    <div class="banner">Welcome!</div>
{elif user_logged_in}
    <div>Hello, {user.name}!</div>
{else}
    <div>Please sign in.</div>
{endif}

<!-- Include a component -->
{component Card title="My Card" description="Card content"}

<!-- Escape braces: {{ outputs { -->
```

### Components

Components live in `components/` and are reusable UI pieces:

```
<!-- components/Card.petal -->
---
# Props come from the parent
---

<div class="card">
    <h3>{title}</h3>
    <p>{description}</p>
</div>

<style>
.card {
    padding: 1.5rem;
    border-radius: 12px;
    background: #f8f9fa;
}
</style>
```

### Layouts

Layouts wrap every page with shared structure:

```
<!-- layouts/Base.petal -->
---
# Base layout
---
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    {component Header}
    <main>{slot}</main>
    {component Footer}
</body>
</html>
```

The `{slot}` tag is where page content goes.

### SEO (Automatic!)

Petal automatically generates for every page:

- **`<title>`** tag
- **Meta description**
- **Open Graph** tags (Facebook, LinkedIn)
- **Twitter Card** tags
- **JSON-LD** structured data
- **sitemap.xml**
- **robots.txt**
- **Canonical URLs**
- **Viewport** and charset

Configure global SEO in `petal.config`:

```
site_name = "My Website"
site_url = "https://mysite.com"
site_description = "A fast website built with Petal"
author = "Abhijeet"
language = "en"
twitter_handle = "@myhandle"
```

### File-Based Routing

| File | URL |
|---|---|
| `pages/index.petal` | `/` |
| `pages/about.petal` | `/about` |
| `pages/blog/index.petal` | `/blog` |
| `pages/blog/[slug].petal` | `/blog/:slug` (dynamic) |
| `pages/api/greet.petal` | `/api/greet` (API route) |

### Dynamic Routes

For dynamic pages like blog posts, define a `pages` list in frontmatter:

```
---
pages = [
    {"slug": "hello-world", "title": "Hello World", "content": "..."},
    {"slug": "why-petal", "title": "Why Petal?", "content": "..."},
]
---

<article>
    <h1>{title}</h1>
    <div>{content}</div>
</article>
```

### API Routes

API endpoints live in `pages/api/`:

```
---
# API route: pages/api/greet.petal
---
response.json({"message": "Hello, " + request.query["name"]})
```

### Server-Side Rendering (SSR)

Add `ssr = True` to frontmatter for pages that should render dynamically on every request:

```
---
ssr = True
title = "Dynamic Page"
---

<h1>Current time: {time}</h1>
```

## Project Structure

```
my-website/
├── pages/              # Each file becomes a route
│   ├── index.petal     # → /
│   ├── about.petal     # → /about
│   └── blog/
│       ├── index.petal # → /blog
│       └── [slug].petal # → /blog/:slug (dynamic)
├── components/         # Reusable UI components
│   ├── Header.petal
│   ├── Footer.petal
│   └── Card.petal
├── layouts/            # Page wrappers
│   └── Base.petal
├── static/             # CSS, images, fonts
│   └── style.css
└── petal.config        # Site settings
```

## How It Works

1. **You write** `.petal` files with Python-like frontmatter + HTML templates
2. **Petal compiles** everything to pure static HTML at build time
3. **Zero JavaScript** is shipped to the browser
4. **SEO tags** are automatically injected into every page
5. **Result:** Lightning-fast pages that search engines love

```
.petal files  →  Petal compiler  →  Static HTML + CSS
                                     ├── index.html
                                     ├── about/index.html
                                     ├── blog/hello/index.html
                                     ├── sitemap.xml
                                     └── robots.txt
```

## Running Petal Scripts

Petal isn't just for websites — it's a general-purpose scripting language:

```bash
python petal.py script.petal   # run a file
python petal.py                # start the REPL
```

### Example Scripts

**Hello World:**
```petal
name = "world"
print(f"Hello, {name}!")
```

**FizzBuzz:**
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

**Fibonacci:**
```petal
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

for i in range(10):
    print(fib(i))
```

## Browser Playground

The `playground.html` file provides an in-browser IDE powered by Pyodide (Python compiled to WebAssembly). Features:

- Live code editing with Python-aware indentation
- Pre-loaded example programs
- Real-time output display
- Syntax error reporting
- No server required — everything runs client-side

## Running Tests

```bash
python test_petal.py
```

The test suite covers:

- Core language features (variables, arithmetic, strings, control flow, functions, closures)
- Advanced features (default args, dot-access, builtins like `enumerate`, `zip`, `isinstance`)
- Web framework (components, templates, routing, SEO)
- Full-stack features (API routes, SSR, environment loading, `fetch` builtin)

## What's Inside

| File | What it does | Lines |
|---|---|---|
| `petal.py` | Core language: lexer, parser, interpreter, REPL | ~1,400 |
| `petal_web.py` | Web framework: components, templates, routing, SSG, SSR, dev server | ~1,330 |
| `petal_seo.py` | SEO engine: meta tags, Open Graph, sitemaps, JSON-LD | ~225 |
| `petal_cli.py` | CLI tool: new, dev, build, preview, start, run | ~305 |
| `petal_env.py` | `.env` file loader | ~37 |
| `playground.html` | Browser-based playground (Pyodide/WASM) | — |
| `test_petal.py` | Comprehensive test suite (48 tests) | ~620 |
| `starter/` | Default project template | — |
| `examples/` | Sample `.petal` programs | — |

**Total: ~4,800+ lines of clean, well-documented Python.**

## Architecture

### Core Language (`petal.py`)

1. **Lexer** (~lines 65–255): Tokenizes source code, handles indentation, strings, numbers, operators
2. **Parser** (~lines 399–688): Builds an abstract syntax tree (AST) from tokens
3. **Interpreter** (~lines 764–1405): Tree-walking interpreter with environment-based scoping, closures, built-ins
4. **CLI/REPL** (bottom of file): Command-line interface and interactive REPL

### Web Framework (`petal_web.py`)

1. **PetalComponent**: Parses `.petal` files into frontmatter + template + style
2. **TemplateEngine**: Evaluates `{expressions}`, `{for}`, `{if}`, `{component}` in HTML
3. **Router**: File-based routing from `pages/` directory (static + dynamic + API)
4. **StaticSiteGenerator**: Builds all pages to static HTML with SEO injection
5. **DevServer**: Local HTTP server with file watching and auto-rebuild
6. **PetalFullStackHandler**: Hybrid static + SSR + API server for production

## Examples

See the `examples/` directory and `starter/` template for working examples.

## Contributing

Contributions are welcome! Here are some ways you can help:

- **Report bugs**: Open an issue with a minimal reproducible example
- **Add features**: Extend the language with new syntax or built-ins
- **Improve documentation**: Clarify examples or add tutorials
- **Optimize performance**: Profile and improve the interpreter
- **Add tests**: Expand the test suite

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Petal is released under the **MIT License**. See [LICENSE](LICENSE) for details.

## Inspiration

Petal draws inspiration from:

- **Python**: Clean syntax, dynamic typing, readability
- **Lua**: Minimal, embeddable, single-file implementation
- **Scheme**: Closures, first-class functions, elegant semantics
- **Astro**: Component islands, SSG-first architecture
- **Next.js**: File-based routing, SSR, API routes

## Roadmap

Potential future enhancements:

- [x] Module system (`import`, `from`)
- [x] Multi-line strings (`"""..."""`)
- [x] Default function arguments
- [x] Full-stack web framework
- [x] Server-side rendering (SSR)
- [x] API routes
- [x] Automatic SEO (Open Graph, Twitter Cards, JSON-LD)
- [x] Static site generation
- [ ] Exception handling (`try`/`except`)
- [ ] Classes and objects
- [ ] Decorators
- [ ] Async/await
- [ ] Performance optimizations (bytecode compilation, JIT)

## FAQ

**Q: Why create another programming language?**
A: Petal is designed as both a learning tool and a minimal, embeddable scripting language. It's small enough to understand completely, yet capable enough to solve real problems — including full-stack web development.

**Q: Can I use Petal in production?**
A: Petal is suitable for scripting, static sites, and small web applications. For performance-critical applications, consider languages like Python, Node.js, or Go. Petal's output is pure HTML/CSS, so it's as fast as any static site.

**Q: How do I extend Petal?**
A: The implementation is intentionally readable. You can add new operators, built-in functions, or language features by modifying `petal.py`. For web features, modify `petal_web.py`.

**Q: Can Petal run in the browser?**
A: Yes! The `playground.html` file runs Petal in the browser via Pyodide. The language itself runs with any Python 3 interpreter.

**Q: Does Petal output JavaScript?**
A: No. Petal compiles to pure HTML and CSS. Zero JavaScript is shipped to the browser.

---

**Built with 🌸 by [Abhijeet](https://github.com/abhijeet-x-ai) and the Petal community.**

*Petal is open source and welcomes contributions from developers of all skill levels.*
