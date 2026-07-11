# Petal Web Framework Design Document

## Vision
Transform Petal from a simple scripting language into a world-first, easy-to-understand web development language. It will combine the simplicity of Python with the performance and SEO capabilities of Astro.js, providing a unified frontend and backend experience.

## Core Principles
1. **Simplicity First**: The syntax must remain clean and intuitive.
2. **SEO by Default**: Built-in metadata, sitemaps, and semantic HTML generation.
3. **Zero-JS by Default**: Like Astro, ship zero JavaScript to the client unless explicitly requested.
4. **Unified Full-Stack**: Write backend logic and frontend templates in the same file.
5. **Fast Loading**: Static Site Generation (SSG) and Server-Side Rendering (SSR) support.

## Language Extensions Required

To support web development, Petal needs the following extensions:

### 1. Component Syntax (Petal Components - `.petal` files)
Similar to Astro or Svelte, a Petal component will have two parts:
- **Server Script**: Backend logic (data fetching, variables)
- **Template**: HTML with Petal expressions

```petal
---
# Server Script (Backend Logic)
title = "My Awesome Blog"
description = "The best blog built with Petal"
posts = fetch_posts()
---
# Template (Frontend)
<html>
  <head>
    <title>{title}</title>
    <meta name="description" content="{description}">
  </head>
  <body>
    <h1>{title}</h1>
    <ul>
      {% for post in posts %}
        <li><a href="/post/{post.id}">{post.title}</a></li>
      {% endfor %}
    </ul>
  </body>
</html>
```

### 2. Built-in Web Functions
- `fetch(url)`: For API calls
- `render(template, data)`: For rendering HTML
- `route(path, handler)`: For defining routes
- `seo(title, desc, keywords)`: Helper for generating SEO meta tags

### 3. File-Based Routing
Like Next.js or Astro, the file structure dictates the routes:
```
pages/
  index.petal       -> /
  about.petal       -> /about
  blog/
    [slug].petal    -> /blog/hello-world
```

## Implementation Strategy

### Phase 1: The Petal Web Server
We need to extend `petal.py` to include a lightweight HTTP server (using Python's `http.server` or `wsgiref` for simplicity, or a custom implementation).

### Phase 2: The Template Engine
We need a parser that can separate the `---` frontmatter (server logic) from the HTML template, evaluate the Petal code, and inject the variables into the HTML.

### Phase 3: Static Site Generation (SSG)
A build command (`petal build`) that evaluates all `.petal` files in the `pages/` directory and outputs pure, fast-loading HTML files.

### Phase 4: SEO Optimization
Built-in components or functions that automatically generate:
- `<title>` and `<meta>` tags
- Open Graph (OG) tags for social media
- `robots.txt` and `sitemap.xml`

## Example: A Complete Petal Web App

**`pages/index.petal`**
```petal
---
site_name = "PetalWeb"
tagline = "The easiest way to build fast websites"
features = ["Simple", "Fast", "SEO-Friendly"]
---
<!DOCTYPE html>
<html lang="en">
<head>
    {seo(title=site_name, description=tagline)}
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: auto; }
    </style>
</head>
<body>
    <header>
        <h1>{site_name}</h1>
        <p>{tagline}</p>
    </header>
    <main>
        <h2>Features</h2>
        <ul>
            {% for feature in features %}
                <li>{feature}</li>
            {% endfor %}
        </ul>
    </main>
</body>
</html>
```

## Next Steps
1. Modify `petal.py` to support the `---` frontmatter syntax.
2. Implement the template rendering engine.
3. Build the development server (`petal dev`).
4. Build the static generator (`petal build`).
