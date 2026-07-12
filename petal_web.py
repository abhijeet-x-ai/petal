#!/usr/bin/env python3
"""
Petal Web Framework — Build SEO-optimized websites with the world's easiest language.

This module provides:
  - PetalComponent: Parses .petal web components (frontmatter + template + style)
  - TemplateEngine: Evaluates {expressions}, {for}, {if}, {component} in HTML
  - Router: File-based routing from pages/ directory
  - StaticSiteGenerator: Builds all pages to static HTML
  - DevServer: Local HTTP server for development with auto-rebuild
  - LayoutEngine: Wraps pages in reusable layouts

Usage:
    from petal_web import StaticSiteGenerator
    ssg = StaticSiteGenerator("my-site/")
    ssg.build()
"""

import os
import re
import sys
import json
import time
import shutil
import hashlib
import threading
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Add parent dir to path for petal imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from petal import Lexer, Parser, Interpreter, Environment, PetalError, run_source
from petal_env import load_dotenv
from petal_seo import (SEOConfig, PageSEO, SEOGenerator, SitemapGenerator,
                       RobotsGenerator, seo_builtin)


def _safe_print(msg=""):
    """Print that handles Windows encoding gracefully."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


class PetalRequest:
    def __init__(self, method, url_path, query, body, headers):
        self._petal_attributes = {
            "method": method,
            "path": url_path,
            "query": query or {},
            "body": body,
            "headers": headers or {},
        }
        self._petal_methods = {}


class PetalResponse:
    def __init__(self):
        self.status_code = 200
        self.response_body = ""
        self.response_headers = {"Content-Type": "text/html; charset=utf-8"}
        self._petal_attributes = {}
        self._petal_methods = {
            "status": self.status,
            "json": self.json,
            "send": self.send,
            "setHeader": self.set_header,
        }
        
    def status(self, code):
        self.status_code = int(code)
        return self
        
    def json(self, data):
        import json
        self.response_body = json.dumps(data)
        self.response_headers["Content-Type"] = "application/json"
        return self
        
    def send(self, body):
        self.response_body = str(body)
        return self
        
    def set_header(self, name, value):
        self.response_headers[str(name)] = str(value)
        return self


# =====================================================================
# Component Parser
# =====================================================================

class PetalComponent:
    """Parses a .petal web component file.
    
    Format:
        ---
        # Petal server-side code (frontmatter)
        title = "My Page"
        ---
        
        <html>
          <h1>{title}</h1>
        </html>
        
        <style>
          h1 { color: blue; }
        </style>
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.frontmatter = ""
        self.template = ""
        self.style = ""
        self.raw = ""
        self._parse()

    def _parse(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.raw = f.read()

        content = self.raw
        
        # Extract frontmatter (between --- markers)
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            self.frontmatter = fm_match.group(1)
            content = content[fm_match.end():]
        
        # Extract <style> block
        style_match = re.search(r'<style\b[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
        if style_match:
            self.style = style_match.group(1).strip()
            content = content[:style_match.start()] + content[style_match.end():]
        
        self.template = content.strip()


# =====================================================================
# Template Engine
# =====================================================================

class TemplateEngine:
    """Evaluates Petal expressions inside HTML templates.
    
    Syntax:
        {variable}              - Output a value
        {expression}            - Evaluate and output
        {for x in list}...{endfor}  - Loop
        {if cond}...{elif cond}...{else}...{endif}  - Conditional
        {component Name prop=val}   - Include a component
        {slot}                  - Content insertion point (in layouts)
    """

    def __init__(self, components=None, layouts=None):
        self.components = components or {}  # name -> PetalComponent
        self.layouts = layouts or {}        # name -> PetalComponent

    def render(self, template, context, seo_gen=None, page_seo=None, page_url=""):
        """Render a template string with the given context dict."""
        result = self._process_blocks(template, context)
        
        # Inject SEO tags if we find a </head> tag
        if seo_gen and page_seo and "</head>" in result:
            seo_tags = seo_gen.generate_meta_tags(page_seo, page_url)
            jsonld = seo_gen.generate_jsonld(page_seo, page_url)
            seo_block = f"    {seo_tags}\n    {jsonld}\n  "
            result = result.replace("</head>", f"{seo_block}</head>")
        
        return result

    def _process_blocks(self, template, context):
        """Process all template blocks: {for}, {if}, {component}, {expressions}."""
        result = []
        i = 0
        n = len(template)

        while i < n:
            if template[i] == '{' and i + 1 < n and template[i+1] != '{':
                # Find the matching closing brace
                end = self._find_closing_brace(template, i)
                if end == -1:
                    result.append(template[i])
                    i += 1
                    continue
                
                tag_content = template[i+1:end].strip()
                
                # {for var in iterable}
                for_match = re.match(r'^for\s+(\w+)\s+in\s+(.+)$', tag_content)
                if for_match:
                    var_name = for_match.group(1)
                    iterable_expr = for_match.group(2)
                    block, after = self._extract_block(template, end + 1, "endfor")
                    iterable = self._eval_expr(iterable_expr, context)
                    for item in iterable:
                        loop_ctx = dict(context)
                        loop_ctx[var_name] = item
                        result.append(self._process_blocks(block, loop_ctx))
                    i = after
                    continue

                # {if condition}
                if_match = re.match(r'^if\s+(.+)$', tag_content)
                if if_match:
                    condition = if_match.group(1)
                    branches, after = self._extract_if_block(template, end + 1)
                    rendered = False
                    
                    # Check main if condition
                    if self._eval_bool(condition, context):
                        result.append(self._process_blocks(branches[0][1], context))
                        rendered = True
                    else:
                        # Check elif branches
                        for branch_type, branch_body, branch_cond in branches[1:]:
                            if branch_type == "elif" and not rendered:
                                if self._eval_bool(branch_cond, context):
                                    result.append(self._process_blocks(branch_body, context))
                                    rendered = True
                                    break
                            elif branch_type == "else" and not rendered:
                                result.append(self._process_blocks(branch_body, context))
                                rendered = True
                                break
                    i = after
                    continue

                # {component Name prop1=val1 prop2=val2}
                comp_match = re.match(r'^component\s+(\w+)(.*)$', tag_content)
                if comp_match:
                    comp_name = comp_match.group(1)
                    props_str = comp_match.group(2).strip()
                    props = self._parse_props(props_str, context)
                    rendered = self._render_component(comp_name, props, context)
                    result.append(rendered)
                    i = end + 1
                    continue

                # {slot} - placeholder for layout content
                if tag_content == "slot":
                    result.append(context.get("__slot_content__", ""))
                    i = end + 1
                    continue

                # Simple expression: {variable} or {expr}
                try:
                    value = self._eval_expr(tag_content, context)
                    if value is None:
                        result.append("")
                    else:
                        result.append(self._html_escape(str(value)))
                except Exception:
                    result.append(f"{{{tag_content}}}")
                i = end + 1
            elif template[i] == '{' and i + 1 < n and template[i+1] == '{':
                # Escaped brace: {{ -> {
                result.append('{')
                i += 2
            else:
                result.append(template[i])
                i += 1

        return "".join(result)

    def _find_closing_brace(self, template, start):
        """Find matching } for { at position start."""
        depth = 0
        i = start
        in_string = False
        string_char = None
        while i < len(template):
            c = template[i]
            if in_string:
                if c == '\\':
                    i += 2
                    continue
                if c == string_char:
                    in_string = False
            else:
                if c in ('"', "'"):
                    in_string = True
                    string_char = c
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return i
            i += 1
        return -1

    def _extract_block(self, template, start, end_tag):
        """Extract content between current position and {endtag}."""
        pattern = re.compile(r'\{' + end_tag + r'\}')
        match = pattern.search(template, start)
        if match:
            return template[start:match.start()], match.end()
        return template[start:], len(template)

    def _extract_if_block(self, template, start):
        """Extract all branches of an if/elif/else/endif block."""
        branches = []
        depth = 0
        current_start = start
        current_type = "if"
        current_cond = ""
        i = start

        while i < len(template):
            if template[i] == '{':
                end = self._find_closing_brace(template, i)
                if end == -1:
                    i += 1
                    continue
                tag = template[i+1:end].strip()

                if re.match(r'^if\s+', tag):
                    depth += 1
                elif tag == "endif":
                    if depth == 0:
                        branches.append((current_type, template[current_start:i], current_cond))
                        return branches, end + 1
                    depth -= 1
                elif depth == 0:
                    elif_match = re.match(r'^elif\s+(.+)$', tag)
                    if elif_match:
                        branches.append((current_type, template[current_start:i], current_cond))
                        current_type = "elif"
                        current_cond = elif_match.group(1)
                        current_start = end + 1
                    elif tag == "else":
                        branches.append((current_type, template[current_start:i], current_cond))
                        current_type = "else"
                        current_cond = ""
                        current_start = end + 1
                i = end + 1
            else:
                i += 1

        # No {endif} found — treat rest as the block
        branches.append((current_type, template[current_start:], current_cond))
        return branches, len(template)

    def _parse_props(self, props_str, context):
        """Parse prop1=val1 prop2="val2" into a dict."""
        props = {}
        if not props_str:
            return props
        # Match key=value or key="value with spaces"
        pattern = re.compile(r'(\w+)\s*=\s*(?:"([^"]*?)"|\'([^\']*?)\'|(\S+))')
        for m in pattern.finditer(props_str):
            key = m.group(1)
            value = m.group(2) or m.group(3) or m.group(4)
            # Try to evaluate as expression
            try:
                value = self._eval_expr(value, context)
            except Exception:
                pass
            props[key] = value
        return props

    def _render_component(self, name, props, parent_context):
        """Render a named component with the given props."""
        if name not in self.components:
            return f'<!-- Component "{name}" not found -->'
        
        comp = self.components[name]
        # Build context from props + parent context
        ctx = dict(parent_context)
        ctx.update(props)
        
        # Execute frontmatter to get component variables
        if comp.frontmatter:
            fm_ctx = self._exec_frontmatter(comp.frontmatter, ctx)
            ctx.update(fm_ctx)
        
        # Render component template
        rendered = self._process_blocks(comp.template, ctx)
        
        # Add scoped styles if any
        if comp.style:
            rendered += f"\n<style>{comp.style}</style>"
        
        return rendered

    def _eval_expr(self, expr_str, context):
        """Evaluate a Petal expression in the given context."""
        expr_str = expr_str.strip()
        
        # Handle dot-access for dicts: post.title -> post["title"]
        # Simple variable lookup
        if expr_str in context:
            return context[expr_str]
        
        # Dot-access: a.b.c
        if re.match(r'^[a-zA-Z_]\w*(\.\w+)+$', expr_str):
            parts = expr_str.split(".")
            value = context.get(parts[0])
            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value
        
        # Use the Petal interpreter for complex expressions
        try:
            output = []
            interp = Interpreter(output_fn=lambda t: output.append(t))
            # Inject context as variables
            for k, v in context.items():
                if isinstance(k, str) and k.isidentifier():
                    interp.globals.assign(k, v)
            
            # Wrap in print to capture the value
            code = f"__result__ = {expr_str}"
            tokens = Lexer(code).tokenize()
            program = Parser(tokens).parse_program()
            interp.run(program)
            return interp.globals.get("__result__", None)
        except Exception:
            return expr_str

    def _eval_bool(self, expr_str, context):
        """Evaluate an expression as a boolean."""
        value = self._eval_expr(expr_str, context)
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    def _exec_frontmatter(self, code, initial_context=None):
        """Execute Petal frontmatter code and return the resulting variables."""
        context = {}
        output = []
        interp = Interpreter(output_fn=lambda t: output.append(t))
        
        # Inject initial context
        if initial_context:
            for k, v in initial_context.items():
                if isinstance(k, str) and k.isidentifier():
                    interp.globals.assign(k, v)
        
        # Add seo() builtin
        interp.globals.assign("seo", seo_builtin)
        
        try:
            tokens = Lexer(code).tokenize()
            program = Parser(tokens).parse_program()
            interp.run(program)
            
            # Extract all variables from the global scope
            for k, v in interp.globals.vars.items():
                if not callable(v) or k == "seo":
                    context[k] = v
        except PetalError as e:
            context["__error__"] = str(e)
        
        return context

    def _html_escape(self, text):
        """Escape HTML characters in output."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


# =====================================================================
# File-Based Router
# =====================================================================

class Router:
    """Maps pages/ directory structure to URL routes.
    
    Routing rules:
        pages/index.petal        -> /
        pages/about.petal        -> /about
        pages/blog/index.petal   -> /blog
        pages/blog/[slug].petal  -> /blog/:slug (dynamic)
    """

    def __init__(self, pages_dir):
        self.pages_dir = Path(pages_dir)
        self.routes = []  # list of (url_pattern, filepath, is_dynamic, param_name)

    def discover(self):
        """Scan pages/ directory and build route table."""
        self.routes = []
        if not self.pages_dir.exists():
            return
        
        for filepath in sorted(self.pages_dir.rglob("*.petal")):
            rel = filepath.relative_to(self.pages_dir)
            parts = list(rel.parts)
            
            # Exclude API routes
            if parts and parts[0] == "api":
                continue
                
            # Convert file path to URL
            filename = parts[-1]
            name = filename.replace(".petal", "")
            
            # Check for dynamic route: [slug].petal
            is_dynamic = name.startswith("[") and name.endswith("]")
            param_name = name[1:-1] if is_dynamic else None
            
            # Build URL path
            url_parts = parts[:-1]  # directory parts
            if name == "index":
                url = "/" + "/".join(url_parts)
            elif is_dynamic:
                url = "/" + "/".join(url_parts + [f":{param_name}"])
            else:
                url = "/" + "/".join(url_parts + [name])
            
            # Normalize
            url = url.replace("//", "/")
            if url != "/" and url.endswith("/"):
                url = url.rstrip("/")
            
            self.routes.append({
                "url": url,
                "filepath": str(filepath),
                "is_dynamic": is_dynamic,
                "param_name": param_name,
                "rel_path": str(rel),
            })
        
        return self.routes

    def discover_api(self):
        """Scan pages/api directory and build API route table."""
        api_routes = []
        api_dir = self.pages_dir / "api"
        if not api_dir.exists():
            return []
            
        for filepath in sorted(api_dir.rglob("*.petal")):
            rel = filepath.relative_to(self.pages_dir)
            parts = list(rel.parts)
            
            filename = parts[-1]
            name = filename.replace(".petal", "")
            
            is_dynamic = name.startswith("[") and name.endswith("]")
            param_name = name[1:-1] if is_dynamic else None
            
            url_parts = parts[:-1]
            # parts[0] is "api"
            if name == "index":
                url = "/api/" + "/".join(url_parts[1:])
            elif is_dynamic:
                url = "/api/" + "/".join(url_parts[1:] + [f":{param_name}"])
            else:
                url = "/api/" + "/".join(url_parts[1:] + [name])
                
            # Normalize
            url = url.replace("//", "/")
            if url.endswith("/") and url != "/":
                url = url.rstrip("/")
                
            api_routes.append({
                "url": url,
                "filepath": str(filepath),
                "is_dynamic": is_dynamic,
                "param_name": param_name,
                "rel_path": str(rel),
            })
        return api_routes

    def get_static_routes(self):
        """Return only static (non-dynamic) routes."""
        return [r for r in self.routes if not r["is_dynamic"]]

    def get_dynamic_routes(self):
        """Return only dynamic routes."""
        return [r for r in self.routes if r["is_dynamic"]]


# =====================================================================
# Layout Engine
# =====================================================================

class LayoutEngine:
    """Wraps page content in a layout template."""

    def __init__(self, layouts_dir):
        self.layouts_dir = Path(layouts_dir)
        self.layouts = {}

    def load(self):
        """Load all layout files."""
        if not self.layouts_dir.exists():
            return
        for filepath in self.layouts_dir.glob("*.petal"):
            name = filepath.stem
            self.layouts[name] = PetalComponent(str(filepath))

    def wrap(self, content, layout_name, context, template_engine,
             seo_gen=None, page_seo=None, page_url=""):
        """Wrap page content in the specified layout."""
        if layout_name not in self.layouts:
            return content
        
        layout = self.layouts[layout_name]
        ctx = dict(context)
        ctx["__slot_content__"] = content
        
        # Execute layout frontmatter
        if layout.frontmatter:
            fm_ctx = template_engine._exec_frontmatter(layout.frontmatter, ctx)
            ctx.update(fm_ctx)
            ctx["__slot_content__"] = content  # Preserve slot content
        
        rendered = template_engine.render(layout.template, ctx,
                                          seo_gen=seo_gen, page_seo=page_seo,
                                          page_url=page_url)
        
        if layout.style:
            rendered = rendered.replace("</head>", f"<style>{layout.style}</style>\n</head>")
        
        return rendered


# =====================================================================
# Static Site Generator
# =====================================================================

class StaticSiteGenerator:
    """Builds a Petal project to static HTML files.
    
    Project structure:
        project/
        ├── pages/          # Route pages
        ├── components/     # Reusable components
        ├── layouts/        # Layout templates
        ├── static/         # Static assets (CSS, images, etc.)
        └── petal.config    # Site configuration
    """

    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.dist_dir = self.project_dir / "dist"
        self.pages_dir = self.project_dir / "pages"
        self.components_dir = self.project_dir / "components"
        self.layouts_dir = self.project_dir / "layouts"
        self.static_dir = self.project_dir / "static"
        self.config_file = self.project_dir / "petal.config"

        self.config = None
        self.seo_config = None
        self.seo_gen = None
        self.router = None
        self.layout_engine = None
        self.template_engine = None

    def build(self):
        """Build the entire site to dist/."""
        start_time = time.time()
        _safe_print(f"\nPetal -- Building your site...\n")

        # Load configuration
        self._load_config()
        
        # Setup router
        self.router = Router(self.pages_dir)
        routes = self.router.discover()
        
        # Load components
        components = self._load_components()
        
        # Load layouts
        self.layout_engine = LayoutEngine(self.layouts_dir)
        self.layout_engine.load()
        
        # Setup template engine
        self.template_engine = TemplateEngine(
            components=components,
            layouts=self.layout_engine.layouts,
        )
        
        # Clean dist/
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir(parents=True)
        
        # Build each page
        built_pages = []
        for route in routes:
            if route["is_dynamic"]:
                # Dynamic routes need data — build from frontmatter
                pages = self._build_dynamic_route(route)
                built_pages.extend(pages)
            else:
                page = self._build_page(route)
                if page:
                    built_pages.append(page)
        
        # Copy static assets
        self._copy_static()
        
        # Generate sitemap.xml
        self._generate_sitemap(built_pages)
        
        # Generate robots.txt
        self._generate_robots()
        
        elapsed = time.time() - start_time
        _safe_print(f"\n  Done! Built {len(built_pages)} pages in {elapsed:.2f}s")
        _safe_print(f"  Output: {self.dist_dir}")
        
        return built_pages

    def _load_config(self):
        """Load petal.config file."""
        load_dotenv(self.project_dir)
        self.config = {
            "site_name": "My Petal Site",
            "site_url": "",
            "site_description": "",
            "author": "",
            "language": "en",
            "layout": "Base",
            "twitter_handle": "",
        }
        
        if self.config_file.exists():
            output = []
            interp = Interpreter(output_fn=lambda t: output.append(t))
            try:
                with open(self.config_file) as f:
                    source = f.read()
                tokens = Lexer(source).tokenize()
                program = Parser(tokens).parse_program()
                interp.run(program)
                for k, v in interp.globals.vars.items():
                    if not callable(v):
                        self.config[k] = v
            except PetalError as e:
                _safe_print(f"  [!] Config error: {e}")
        
        self.seo_config = SEOConfig(
            site_name=self.config.get("site_name", ""),
            site_url=self.config.get("site_url", ""),
            site_description=self.config.get("site_description", ""),
            author=self.config.get("author", ""),
            language=self.config.get("language", "en"),
            twitter_handle=self.config.get("twitter_handle", ""),
        )
        self.seo_gen = SEOGenerator(self.seo_config)

    def _load_components(self):
        """Load all component files."""
        components = {}
        if self.components_dir.exists():
            for filepath in self.components_dir.glob("*.petal"):
                name = filepath.stem
                components[name] = PetalComponent(str(filepath))
                _safe_print(f"  [+] Component: {name}")
        return components

    def _build_page(self, route):
        """Build a single page."""
        filepath = route["filepath"]
        url = route["url"]
        
        comp = PetalComponent(filepath)
        
        # Execute frontmatter
        context = dict(self.config)
        if comp.frontmatter:
            fm_ctx = self.template_engine._exec_frontmatter(comp.frontmatter, context)
            context.update(fm_ctx)
        
        # Check for SEO data from seo() call
        page_seo = None
        for k, v in context.items():
            if isinstance(v, PageSEO):
                page_seo = v
                break
        
        if page_seo is None:
            page_seo = PageSEO(
                title=context.get("title", ""),
                description=context.get("description", ""),
            )
        
        # Render template (without SEO - page template usually lacks </head>)
        rendered = self.template_engine.render(
            comp.template, context
        )
        
        # Add component styles
        if comp.style:
            if "</head>" in rendered:
                rendered = rendered.replace("</head>", f"<style>{comp.style}</style>\n</head>")
            else:
                rendered += f"\n<style>{comp.style}</style>"
        
        # Wrap in layout (with SEO injection - layout has </head>)
        layout_name = context.get("layout", self.config.get("layout", ""))
        if layout_name and layout_name in self.layout_engine.layouts:
            rendered = self.layout_engine.wrap(
                rendered, layout_name, context, self.template_engine,
                seo_gen=self.seo_gen, page_seo=page_seo, page_url=url
            )
        else:
            # No layout - inject SEO directly if </head> exists
            if "</head>" in rendered and self.seo_gen and page_seo:
                seo_tags = self.seo_gen.generate_meta_tags(page_seo, url)
                jsonld = self.seo_gen.generate_jsonld(page_seo, url)
                seo_block = f"    {seo_tags}\n    {jsonld}\n  "
                rendered = rendered.replace("</head>", f"{seo_block}</head>")
        
        # Write to dist/
        if url == "/":
            out_path = self.dist_dir / "index.html"
        else:
            out_dir = self.dist_dir / url.lstrip("/")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "index.html"
        
        # Add doctype if missing
        if not rendered.strip().lower().startswith("<!doctype") and not rendered.strip().lower().startswith("<html"):
            rendered = "<!DOCTYPE html>\n" + rendered
        
        out_path.write_text(rendered, encoding="utf-8")
        _safe_print(f"  [>] {url} -> {out_path.relative_to(self.dist_dir)}")
        
        return {"url": url, "filepath": str(out_path), "title": page_seo.title}

    def _build_dynamic_route(self, route):
        """Build pages for a dynamic route like [slug].petal.
        
        The frontmatter must define a `pages` list of dicts, each with
        the dynamic param and any page-specific data.
        """
        filepath = route["filepath"]
        param_name = route["param_name"]
        
        comp = PetalComponent(filepath)
        
        # Execute frontmatter to get the pages list
        context = dict(self.config)
        if comp.frontmatter:
            fm_ctx = self.template_engine._exec_frontmatter(comp.frontmatter, context)
            context.update(fm_ctx)
        
        pages_data = context.get("pages", [])
        if not isinstance(pages_data, list):
            _safe_print(f"  [!] Dynamic route {route['url']} has no 'pages' list in frontmatter")
            return []
        
        built = []
        for page_data in pages_data:
            if not isinstance(page_data, dict):
                continue
            
            param_value = page_data.get(param_name, "")
            if not param_value:
                continue
            
            # Build context for this specific page
            page_ctx = dict(context)
            page_ctx.update(page_data)
            page_ctx[param_name] = param_value
            
            # Build URL
            url = route["url"].replace(f":{param_name}", str(param_value))
            
            # Check for SEO data
            page_seo = None
            for k, v in page_ctx.items():
                if isinstance(v, PageSEO):
                    page_seo = v
                    break
            if page_seo is None:
                page_seo = PageSEO(
                    title=page_ctx.get("title", str(param_value)),
                    description=page_ctx.get("description", ""),
                    page_type="article",
                )
            
            # Render (without SEO - page template usually lacks </head>)
            rendered = self.template_engine.render(
                comp.template, page_ctx
            )
            
            if comp.style:
                if "</head>" in rendered:
                    rendered = rendered.replace("</head>", f"<style>{comp.style}</style>\n</head>")
                else:
                    rendered += f"\n<style>{comp.style}</style>"
            
            # Wrap in layout (with SEO injection - layout has </head>)
            layout_name = page_ctx.get("layout", self.config.get("layout", ""))
            if layout_name and layout_name in self.layout_engine.layouts:
                rendered = self.layout_engine.wrap(
                    rendered, layout_name, page_ctx, self.template_engine,
                    seo_gen=self.seo_gen, page_seo=page_seo, page_url=url
                )
            else:
                # No layout - inject SEO directly if </head> exists
                if "</head>" in rendered and self.seo_gen and page_seo:
                    seo_tags = self.seo_gen.generate_meta_tags(page_seo, url)
                    jsonld = self.seo_gen.generate_jsonld(page_seo, url)
                    seo_block = f"    {seo_tags}\n    {jsonld}\n  "
                    rendered = rendered.replace("</head>", f"{seo_block}</head>")
            
            # Write
            out_dir = self.dist_dir / url.lstrip("/")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "index.html"
            
            if not rendered.strip().lower().startswith("<!doctype"):
                rendered = "<!DOCTYPE html>\n" + rendered
            
            out_path.write_text(rendered, encoding="utf-8")
            _safe_print(f"  [>] {url} -> {out_path.relative_to(self.dist_dir)}")
            
            built.append({"url": url, "filepath": str(out_path), "title": page_seo.title})
        
        return built

    def _copy_static(self):
        """Copy static/ directory to dist/."""
        if self.static_dir.exists():
            for item in self.static_dir.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(self.static_dir)
                    dest = self.dist_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
                    _safe_print(f"  [+] static/{rel}")

    def _generate_sitemap(self, pages):
        """Generate sitemap.xml."""
        sitemap_gen = SitemapGenerator(self.seo_config)
        page_entries = []
        for p in pages:
            entry = {"url": p["url"]}
            if p["url"] == "/":
                entry["priority"] = "1.0"
                entry["changefreq"] = "daily"
            else:
                entry["priority"] = "0.7"
            page_entries.append(entry)
        
        sitemap_xml = sitemap_gen.generate(page_entries)
        (self.dist_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
        _safe_print(f"  [+] sitemap.xml ({len(pages)} URLs)")

    def _generate_robots(self):
        """Generate robots.txt."""
        robots_gen = RobotsGenerator(self.seo_config)
        robots_txt = robots_gen.generate()
        (self.dist_dir / "robots.txt").write_text(robots_txt, encoding="utf-8")
        _safe_print(f"  [+] robots.txt")


# =====================================================================
# Full-Stack HTTP Server Handler
# =====================================================================

class PetalFullStackHandler(SimpleHTTPRequestHandler):
    """Hybrid static/SSR/API HTTP server handler."""
    
    def __init__(self, *args, project_dir=None, dist_dir=None, **kwargs):
        self.project_dir = Path(project_dir)
        self.dist_dir = Path(dist_dir)
        self.ssg = StaticSiteGenerator(self.project_dir)
        self.ssg._load_config()
        super().__init__(*args, directory=str(self.dist_dir), **kwargs)

    def do_GET(self):
        self.handle_request("GET")
        
    def do_POST(self):
        self.handle_request("POST")
        
    def do_PUT(self):
        self.handle_request("PUT")
        
    def do_DELETE(self):
        self.handle_request("DELETE")
        
    def handle_request(self, method):
        # 1. Parse URL path and query parameters
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path
        query_dict = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
        
        # 2. Get headers
        headers_dict = dict(self.headers)
        
        # 3. Read body if present
        body = None
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length)
            try:
                body_str = raw_body.decode('utf-8')
                if self.headers.get('Content-Type', '').startswith('application/json'):
                    body = json.loads(body_str)
                else:
                    body = body_str
            except Exception:
                body = raw_body
        
        # 4. Check if it's an API route
        router = Router(self.project_dir / "pages")
        api_routes = router.discover_api()
        
        matched_api = None
        params = {}
        for r in api_routes:
            matched_api, params = self._match_route(path, r["url"])
            if matched_api:
                matched_route = r
                break
                
        if matched_api:
            self._execute_api_route(matched_route, method, path, query_dict, body, headers_dict, params)
            return
            
        # 5. Check if it's an SSR page
        page_routes = router.discover()
        matched_page = None
        params = {}
        for r in page_routes:
            matched_page, params = self._match_route(path, r["url"])
            if matched_page:
                matched_route = r
                break
                
        if matched_page:
            filepath = matched_route["filepath"]
            comp = PetalComponent(filepath)
            
            is_ssr = False
            if comp.frontmatter:
                try:
                    interp = Interpreter(output_fn=lambda x: None)
                    interp.globals.assign("seo", seo_builtin)
                    interp.globals.assign("request", PetalRequest(method, path, query_dict, body, headers_dict))
                    
                    tokens = Lexer(comp.frontmatter).tokenize()
                    program = Parser(tokens).parse_program()
                    interp.run(program)
                    is_ssr = interp.is_truthy(interp.globals.vars.get("ssr", False))
                except Exception:
                    pass
            
            if is_ssr:
                self._execute_ssr_page(matched_route, comp, method, path, query_dict, body, headers_dict, params)
                return
                
        # 6. Fallback to serving static files from dist/
        if method == "GET":
            if path == "/":
                self.path = "/index.html"
            elif not os.path.splitext(path)[1]:
                test_path = self.dist_dir / path.lstrip("/") / "index.html"
                if test_path.exists():
                    self.path = path.rstrip("/") + "/index.html"
                else:
                    test_path = self.dist_dir / (path.lstrip("/") + ".html")
                    if test_path.exists():
                        self.path = path + ".html"
            
            super().do_GET()
        else:
            self.send_error(405, "Method not allowed")

    def _match_route(self, request_path, route_pattern):
        req_parts = [p for p in request_path.strip("/").split("/") if p]
        pat_parts = [p for p in route_pattern.strip("/").split("/") if p]
        
        if len(req_parts) != len(pat_parts):
            return False, {}
            
        params = {}
        for req, pat in zip(req_parts, pat_parts):
            if pat.startswith(":") or (pat.startswith("[") and pat.endswith("]")):
                param_name = pat[1:] if pat.startswith(":") else pat[1:-1]
                params[param_name] = req
            elif req != pat:
                return False, {}
        return True, params

    def _execute_api_route(self, route, method, path, query, body, headers, params):
        combined_query = dict(query)
        combined_query.update(params)
        
        petal_req = PetalRequest(method, path, combined_query, body, headers)
        petal_res = PetalResponse()
        
        try:
            with open(route["filepath"], "r", encoding="utf-8") as f:
                code = f.read()
                
            if code.startswith("---"):
                parts = re.split(r'^---\s*$', code, maxsplit=2, flags=re.MULTILINE)
                if len(parts) >= 3:
                    code = parts[1] + "\n" + parts[2]
            
            interp = Interpreter(output_fn=lambda x: None)
            interp.globals.assign("request", petal_req)
            interp.globals.assign("response", petal_res)
            
            tokens = Lexer(code).tokenize()
            program = Parser(tokens).parse_program()
            interp.run(program)
            
            self.send_response(petal_res.status_code)
            for h_name, h_val in petal_res.response_headers.items():
                self.send_header(h_name, h_val)
            self.end_headers()
            self.wfile.write(petal_res.response_body.encode('utf-8'))
        except PetalError as e:
            self._send_error_json(500, f"Petal Compile Error: {e.format()}")
        except Exception as e:
            self._send_error_json(500, f"Internal Server Error: {e}")

    def _send_error_json(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def _execute_ssr_page(self, route, comp, method, path, query, body, headers, params):
        try:
            combined_query = dict(query)
            combined_query.update(params)
            
            petal_req = PetalRequest(method, path, combined_query, body, headers)
            context = dict(self.ssg.config)
            context["request"] = petal_req
            
            components = self.ssg._load_components()
            self.ssg.layout_engine.load()
            
            template_engine = TemplateEngine(
                components=components,
                layouts=self.ssg.layout_engine.layouts,
            )
            
            if comp.frontmatter:
                fm_ctx = template_engine._exec_frontmatter(
                    comp.frontmatter, 
                    initial_context={"request": petal_req}
                )
                context.update(fm_ctx)
                
            page_seo = None
            for k, v in context.items():
                if isinstance(v, PageSEO):
                    page_seo = v
                    break
            if page_seo is None:
                page_seo = PageSEO(
                    title=context.get("title", ""),
                    description=context.get("description", ""),
                )
                
            rendered = template_engine.render(comp.template, context)
            
            if comp.style:
                if "</head>" in rendered:
                    rendered = rendered.replace("</head>", f"<style>{comp.style}</style>\n</head>")
                else:
                    rendered += f"\n<style>{comp.style}</style>"
                    
            layout_name = context.get("layout", self.ssg.config.get("layout", ""))
            if layout_name and layout_name in self.ssg.layout_engine.layouts:
                rendered = self.ssg.layout_engine.wrap(
                    rendered, layout_name, context, template_engine,
                    seo_gen=self.ssg.seo_gen, page_seo=page_seo, page_url=route["url"]
                )
            else:
                if "</head>" in rendered and self.ssg.seo_gen and page_seo:
                    seo_tags = self.ssg.seo_gen.generate_meta_tags(page_seo, route["url"])
                    jsonld = self.ssg.seo_gen.generate_jsonld(page_seo, route["url"])
                    seo_block = f"    {seo_tags}\n    {jsonld}\n  "
                    rendered = rendered.replace("</head>", f"{seo_block}</head>")
                    
            if not rendered.strip().lower().startswith("<!doctype") and not rendered.strip().lower().startswith("<html"):
                rendered = "<!DOCTYPE html>\n" + rendered
                
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(rendered.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err_html = f"<html><body><h1>SSR Rendering Error</h1><p>{e}</p><pre>{traceback.format_exc()}</pre></body></html>"
            self.wfile.write(err_html.encode('utf-8'))

    def log_message(self, format, *args):
        msg = format % args
        if "200" in msg:
            status = "✅"
        elif "304" in msg:
            status = "🔄"
        elif "404" in msg:
            status = "❌"
        else:
            status = "🔶"
        _safe_print(f"  {status} {self.path}")


class DevServer:
    """Development server with file watching and auto-rebuild."""

    def __init__(self, project_dir, port=3000):
        self.project_dir = Path(project_dir)
        self.port = port
        self.ssg = StaticSiteGenerator(project_dir)
        self._file_hashes = {}

    def start(self):
        """Start the development server."""
        # Initial build
        self.ssg.build()
        self._snapshot_files()

        # Start file watcher in background
        watcher = threading.Thread(target=self._watch_files, daemon=True)
        watcher.start()

        # Start HTTP server
        dist = str(self.ssg.dist_dir)
        project = str(self.project_dir)
        handler = lambda *args, **kwargs: PetalFullStackHandler(*args, project_dir=project, dist_dir=dist, **kwargs)
        
        server = HTTPServer(("localhost", self.port), handler)
        _safe_print(f"\n  Petal dev server running at:")
        _safe_print(f"   http://localhost:{self.port}")
        _safe_print(f"\n   Watching for changes... (Ctrl+C to stop)\n")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            _safe_print("\n\n  Server stopped.")
            server.server_close()

    def _snapshot_files(self):
        """Take a snapshot of all source file hashes."""
        self._file_hashes = {}
        watch_dirs = [self.project_dir / d for d in ["pages", "components", "layouts", "static"]]
        watch_dirs.append(self.project_dir / "petal.config")
        
        for d in watch_dirs:
            if d.is_file():
                self._file_hashes[str(d)] = self._hash_file(d)
            elif d.is_dir():
                for f in d.rglob("*"):
                    if f.is_file():
                        self._file_hashes[str(f)] = self._hash_file(f)

    def _hash_file(self, filepath):
        """Get hash of a file."""
        try:
            return hashlib.md5(filepath.read_bytes()).hexdigest()
        except Exception:
            return ""

    def _watch_files(self):
        """Watch for file changes and rebuild."""
        while True:
            time.sleep(1)
            changed = False
            
            current_hashes = {}
            watch_dirs = [self.project_dir / d for d in ["pages", "components", "layouts", "static"]]
            watch_dirs.append(self.project_dir / "petal.config")
            
            for d in watch_dirs:
                if d.is_file():
                    current_hashes[str(d)] = self._hash_file(d)
                elif d.is_dir():
                    for f in d.rglob("*"):
                        if f.is_file():
                            current_hashes[str(f)] = self._hash_file(f)
            
            if current_hashes != self._file_hashes:
                changed = True
                self._file_hashes = current_hashes
            
            if changed:
                _safe_print("\n  Files changed -- rebuilding...\n")
                try:
                    self.ssg.build()
                except Exception as e:
                    _safe_print(f"  [!] Build error: {e}")


# =====================================================================
# Public API
# =====================================================================

def build_site(project_dir):
    """Build a Petal site to static HTML."""
    ssg = StaticSiteGenerator(project_dir)
    return ssg.build()


def serve_site(project_dir, port=3000):
    """Start the development server."""
    dev = DevServer(project_dir, port=port)
    dev.start()
