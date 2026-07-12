#!/usr/bin/env python3
"""
Petal Test Suite -- Comprehensive tests for the Petal language and web framework.

Run:  python test_petal.py
"""

import os
import sys
import json
import shutil
import traceback
from pathlib import Path

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Results tracking
results = []
output_lines = []


def _out(msg=""):
    output_lines.append(msg)


def test(name, fn):
    """Run a test and track results."""
    try:
        fn()
        results.append(("PASS", name))
        _out(f"  PASS  {name}")
    except Exception as e:
        results.append(("FAIL", name))
        _out(f"  FAIL  {name}")
        _out(f"        {e}")
        _out(f"        {traceback.format_exc().splitlines()[-2]}")


def assert_eq(actual, expected, msg=""):
    if actual != expected:
        raise AssertionError(f"{msg}: expected {expected!r}, got {actual!r}")


def run_petal(source):
    """Run Petal source code and return captured output."""
    from petal import run_source
    output = []
    run_source(source, output_fn=lambda t: output.append(t))
    return output


# ============================================================
# PHASE 1: Core Language Tests
# ============================================================

def test_hello():
    out = run_petal('print("Hello, Petal!")')
    assert_eq(out, ["Hello, Petal!"], "hello output")


def test_variables():
    out = run_petal('x = 42\nprint(x)')
    assert_eq(out, ["42"], "variable output")


def test_arithmetic():
    out = run_petal('print(2 + 3 * 4)')
    assert_eq(out, ["14"], "arithmetic")


def test_strings():
    out = run_petal('print(f"2+3={2+3}")')
    assert_eq(out, ["2+3=5"], "f-string")


def test_lists():
    out = run_petal('nums = [1, 2, 3]\nnums.append(4)\nprint(len(nums))')
    assert_eq(out, ["4"], "list append+len")


def test_dicts():
    out = run_petal('d = {"a": 1, "b": 2}\nprint(d["a"])')
    assert_eq(out, ["1"], "dict access")


def test_if_elif_else():
    out = run_petal('x = 5\nif x > 10:\n    print("big")\nelif x > 3:\n    print("mid")\nelse:\n    print("small")')
    assert_eq(out, ["mid"], "if/elif/else")


def test_for_loop():
    out = run_petal('for i in range(3):\n    print(i)')
    assert_eq(out, ["0", "1", "2"], "for loop")


def test_while_loop():
    out = run_petal('i = 0\nwhile i < 3:\n    print(i)\n    i += 1')
    assert_eq(out, ["0", "1", "2"], "while loop")


def test_functions():
    out = run_petal('def add(a, b):\n    return a + b\nprint(add(3, 4))')
    assert_eq(out, ["7"], "function")


def test_closures():
    out = run_petal('def make_adder(x):\n    def adder(y):\n        return x + y\n    return adder\nadd5 = make_adder(5)\nprint(add5(10))')
    assert_eq(out, ["15"], "closure")


def test_break_continue():
    out = run_petal('for i in range(10):\n    if i == 5:\n        break\n    if i % 2 == 0:\n        continue\n    print(i)')
    assert_eq(out, ["1", "3"], "break/continue")


def test_slicing():
    out = run_petal('print([1,2,3,4,5][1:3])')
    assert_eq(out, ["[2, 3]"], "slicing")


def test_string_methods():
    out = run_petal('print("hello".upper())')
    assert_eq(out, ["HELLO"], "string upper")


def test_in_operator():
    out = run_petal('print("a" in ["a", "b", "c"])')
    assert_eq(out, ["True"], "in operator")


# ---- New language features ----

def test_default_args():
    out = run_petal('def greet(name="world"):\n    print(f"Hello, {name}!")\ngreet()\ngreet("Abhi")')
    assert_eq(out, ["Hello, world!", "Hello, Abhi!"], "default args")


def test_multiline_string():
    out = run_petal('s = """hello\nworld"""\nprint(s)')
    assert_eq(out, ["hello\nworld"], "multi-line string")


def test_dict_dot_access():
    out = run_petal('person = {"name": "Abhi", "age": 25}\nprint(person.name)')
    assert_eq(out, ["Abhi"], "dict dot-access")


def test_string_multiplication():
    out = run_petal('print("ha" * 3)')
    assert_eq(out, ["hahaha"], "string * int")


def test_enumerate_builtin():
    out = run_petal('for pair in enumerate(["a", "b"]):\n    print(pair)')
    assert_eq(out, ['[0, "a"]', '[1, "b"]'], "enumerate")


def test_zip_builtin():
    out = run_petal('for pair in zip([1,2], ["a","b"]):\n    print(pair)')
    assert_eq(out, ['[1, "a"]', '[2, "b"]'], "zip")


def test_isinstance_builtin():
    out = run_petal('print(isinstance(42, "int"))\nprint(isinstance("hi", "str"))\nprint(isinstance(42, "str"))')
    assert_eq(out, ["True", "True", "False"], "isinstance")


def test_reversed_builtin():
    out = run_petal('print(reversed([1, 2, 3]))')
    assert_eq(out, ["[3, 2, 1]"], "reversed")


def test_any_all_builtins():
    out = run_petal('print(any([False, True, False]))\nprint(all([True, True, True]))\nprint(all([True, False]))')
    assert_eq(out, ["True", "True", "False"], "any/all")


def test_extra_string_methods():
    out = run_petal('print("hello".capitalize())\nprint("hello world".title())\nprint("abc".isalpha())')
    assert_eq(out, ["Hello", "Hello World", "True"], "extra string methods")


# ---- Run existing .petal example files ----

def test_example_file(filepath):
    """Run an example .petal file and verify it doesn't crash."""
    from petal import run_source, PetalError
    with open(filepath, "r") as f:
        source = f.read()
    output = []
    run_source(source, output_fn=lambda t: output.append(t))
    if not output:
        raise AssertionError("example produced no output")


# ============================================================
# PHASE 2: Web Framework Tests
# ============================================================

def test_seo_import():
    from petal_seo import SEOConfig, PageSEO, SEOGenerator, SitemapGenerator, RobotsGenerator
    assert_eq(True, True, "SEO import")


def test_seo_meta_tags():
    from petal_seo import SEOConfig, PageSEO, SEOGenerator
    config = SEOConfig(site_name="Test Site", site_url="https://example.com")
    gen = SEOGenerator(config)
    page = PageSEO(title="About", description="About page")
    tags = gen.generate_meta_tags(page, "/about")
    if "<title>" not in tags:
        raise AssertionError("missing <title> tag")
    if "og:title" not in tags:
        raise AssertionError("missing og:title")
    if "twitter:card" not in tags:
        raise AssertionError("missing twitter:card")


def test_seo_jsonld():
    from petal_seo import SEOConfig, PageSEO, SEOGenerator
    config = SEOConfig(site_name="Test", site_url="https://example.com", author="Abhi")
    gen = SEOGenerator(config)
    page = PageSEO(title="My Article", page_type="article")
    jsonld = gen.generate_jsonld(page, "/blog/test")
    if "schema.org" not in jsonld:
        raise AssertionError("missing schema.org")
    if "Article" not in jsonld:
        raise AssertionError("missing Article type")


def test_seo_sitemap():
    from petal_seo import SEOConfig, SitemapGenerator
    config = SEOConfig(site_url="https://example.com")
    gen = SitemapGenerator(config)
    sitemap = gen.generate([{"url": "/"}, {"url": "/about"}])
    if "<urlset" not in sitemap:
        raise AssertionError("missing urlset")
    if "https://example.com/" not in sitemap:
        raise AssertionError("missing root URL")


def test_seo_robots():
    from petal_seo import SEOConfig, RobotsGenerator
    config = SEOConfig(site_url="https://example.com")
    gen = RobotsGenerator(config)
    robots = gen.generate()
    if "User-agent" not in robots:
        raise AssertionError("missing User-agent")
    if "sitemap.xml" not in robots.lower():
        raise AssertionError("missing sitemap reference")


def test_web_import():
    from petal_web import PetalComponent, TemplateEngine, Router, StaticSiteGenerator
    assert_eq(True, True, "web import")


def test_template_variable():
    from petal_web import TemplateEngine
    engine = TemplateEngine()
    result = engine.render("<h1>{title}</h1>", {"title": "Hello"})
    if "Hello" not in result:
        raise AssertionError(f"expected 'Hello' in result, got: {result}")


def test_template_for_loop():
    from petal_web import TemplateEngine
    engine = TemplateEngine()
    template = "{for x in items}<p>{x}</p>{endfor}"
    result = engine.render(template, {"items": ["a", "b", "c"]})
    if "<p>a</p>" not in result or "<p>c</p>" not in result:
        raise AssertionError(f"for loop failed: {result}")


def test_template_if_else():
    from petal_web import TemplateEngine
    engine = TemplateEngine()
    template = "{if show}YES{else}NO{endif}"
    r1 = engine.render(template, {"show": True})
    r2 = engine.render(template, {"show": False})
    assert_eq("YES" in r1, True, "if-true")
    assert_eq("NO" in r2, True, "if-false")


def test_template_dot_access():
    from petal_web import TemplateEngine
    engine = TemplateEngine()
    result = engine.render("<p>{post.title}</p>", {"post": {"title": "My Post"}})
    if "My Post" not in result:
        raise AssertionError(f"dot access failed: {result}")


def test_component_parsing():
    from petal_web import PetalComponent
    import tempfile
    # Write a temp component
    with tempfile.NamedTemporaryFile(mode="w", suffix=".petal", delete=False, encoding="utf-8") as f:
        f.write('---\ntitle = "Test"\n---\n<h1>{title}</h1>\n<style>h1 { color: red; }</style>')
        tmppath = f.name
    try:
        comp = PetalComponent(tmppath)
        assert_eq('title = "Test"' in comp.frontmatter, True, "frontmatter")
        assert_eq("<h1>{title}</h1>" in comp.template, True, "template")
        assert_eq("color: red" in comp.style, True, "style")
    finally:
        os.unlink(tmppath)


def test_router():
    from petal_web import Router
    script_dir = os.path.dirname(os.path.abspath(__file__))
    starter_pages = os.path.join(script_dir, "starter", "pages")
    if os.path.exists(starter_pages):
        router = Router(starter_pages)
        routes = router.discover()
        if len(routes) < 2:
            raise AssertionError(f"expected at least 2 routes, got {len(routes)}")
        urls = [r["url"] for r in routes]
        if "/" not in urls:
            raise AssertionError("missing root route")
    else:
        raise AssertionError("starter/pages not found")


def test_env_builtin():
    import os
    os.environ["TEST_PETAL_KEY"] = "petal_secret_value"
    try:
        out = run_petal('print(env.get("TEST_PETAL_KEY"))')
        assert_eq(out, ["petal_secret_value"], "env builtin lookup")
    finally:
        del os.environ["TEST_PETAL_KEY"]


def test_fetch_builtin():
    import urllib.request
    from urllib.error import HTTPError
    
    orig_urlopen = urllib.request.urlopen
    
    class MockResponse:
        def __init__(self, status, text, headers):
            self.status = status
            self.text = text
            self.headers_dict = headers
            
        def read(self):
            return self.text.encode('utf-8')
            
        def info(self):
            class Info(dict):
                def get_content_charset(self):
                    return "utf-8"
            return Info()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
    def mock_urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req
        if "mock-api.com" in url:
            return MockResponse(200, '{"success": true}', {})
        raise HTTPError(url, 404, "Not Found", {}, None)
        
    urllib.request.urlopen = mock_urlopen
    try:
        out = run_petal('res = fetch("http://mock-api.com")\nprint(res.status)\nprint(res.json()["success"])')
        assert_eq(out, ["200", "True"], "fetch mock success")
    finally:
        urllib.request.urlopen = orig_urlopen


def test_api_routes():
    from petal_web import Router, PetalRequest, PetalResponse
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pages_dir = Path(tmpdir) / "pages"
        api_dir = pages_dir / "api"
        api_dir.mkdir(parents=True)
        
        greet_file = api_dir / "greet.petal"
        greet_file.write_text('response.json({"msg": "Hello " + request.query["name"]})', encoding="utf-8")
        
        router = Router(pages_dir)
        api_routes = router.discover_api()
        assert_eq(len(api_routes), 1, "discover api")
        assert_eq(api_routes[0]["url"], "/api/greet", "api route URL")
        
        from petal import Interpreter, Lexer, Parser
        petal_req = PetalRequest("GET", "/api/greet", {"name": "TestUser"}, None, None)
        petal_res = PetalResponse()
        
        interp = Interpreter(output_fn=lambda x: None)
        interp.globals.assign("request", petal_req)
        interp.globals.assign("response", petal_res)
        
        tokens = Lexer(greet_file.read_text()).tokenize()
        program = Parser(tokens).parse_program()
        interp.run(program)
        
        assert_eq(petal_res.status_code, 200, "API response status")
        assert_eq(petal_res.response_body, '{"msg": "Hello TestUser"}', "API response body")


def test_ssr_page():
    from petal_web import StaticSiteGenerator, PetalRequest
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "pages").mkdir()
        (td / "layouts").mkdir()
        (td / "components").mkdir()
        (td / "static").mkdir()
        
        (td / "layouts" / "Base.petal").write_text('---\n---\n<html><head></head><body>{slot}</body></html>', encoding="utf-8")
        (td / "pages" / "index.petal").write_text('---\nssr = True\ntitle = "SSR Page"\n---\n<h1>Hello from SSR</h1>', encoding="utf-8")
        
        ssg = StaticSiteGenerator(td)
        ssg._load_config()
        
        from petal_web import PetalComponent, TemplateEngine
        comp = PetalComponent(str(td / "pages" / "index.petal"))
        
        petal_req = PetalRequest("GET", "/", {}, None, None)
        context = dict(ssg.config)
        context["request"] = petal_req
        
        template_engine = TemplateEngine()
        fm_ctx = template_engine._exec_frontmatter(comp.frontmatter, {"request": petal_req})
        context.update(fm_ctx)
        
        assert_eq(context.get("ssr"), True, "frontmatter ssr true")
        assert_eq(context.get("title"), "SSR Page", "frontmatter title")


def test_cli_import():
    from petal_cli import main, PETAL_VERSION
    if not PETAL_VERSION:
        raise AssertionError("missing version")


# ============================================================
# PHASE 3: Full Site Build Test
# ============================================================

def test_full_site_build():
    from petal_web import StaticSiteGenerator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    starter_dir = os.path.join(script_dir, "starter")

    # Create a temp copy to avoid modifying starter/
    test_dir = os.path.join(script_dir, "_test_build")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    shutil.copytree(starter_dir, test_dir)

    try:
        ssg = StaticSiteGenerator(test_dir)
        pages = ssg.build()

        if not pages:
            raise AssertionError("no pages built")

        dist_dir = os.path.join(test_dir, "dist")
        index_html = os.path.join(dist_dir, "index.html")
        if not os.path.exists(index_html):
            raise AssertionError("dist/index.html not created")

        # Check index.html has SEO tags
        with open(index_html, "r", encoding="utf-8") as f:
            content = f.read()

        # Title might be in the layout-wrapped page or as a meta tag
        if "<title>" not in content and "og:title" not in content:
            raise AssertionError(f"missing title/og:title in built page. Content starts with: {content[:200]}")
        if "og:title" not in content:
            raise AssertionError("missing og:title in built page")

        # Check sitemap exists
        sitemap = os.path.join(dist_dir, "sitemap.xml")
        if not os.path.exists(sitemap):
            raise AssertionError("sitemap.xml not generated")

        # Check robots.txt exists
        robots = os.path.join(dist_dir, "robots.txt")
        if not os.path.exists(robots):
            raise AssertionError("robots.txt not generated")

        # Check static files copied
        style_css = os.path.join(dist_dir, "style.css")
        if not os.path.exists(style_css):
            raise AssertionError("style.css not copied to dist/")

        _out(f"        Built {len(pages)} pages successfully")

    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


# ============================================================
# Main
# ============================================================

def main():
    _out("=" * 60)
    _out("PETAL COMPREHENSIVE TEST SUITE")
    _out("=" * 60)

    # Phase 1: Core Language
    _out("\n--- Core Language Tests ---")
    test("Hello world", test_hello)
    test("Variables", test_variables)
    test("Arithmetic", test_arithmetic)
    test("F-strings", test_strings)
    test("Lists", test_lists)
    test("Dicts", test_dicts)
    test("If/elif/else", test_if_elif_else)
    test("For loop", test_for_loop)
    test("While loop", test_while_loop)
    test("Functions", test_functions)
    test("Closures", test_closures)
    test("Break/continue", test_break_continue)
    test("Slicing", test_slicing)
    test("String methods", test_string_methods)
    test("In operator", test_in_operator)

    _out("\n--- New Language Features ---")
    test("Default arguments", test_default_args)
    test("Multi-line strings", test_multiline_string)
    test("Dict dot-access", test_dict_dot_access)
    test("String multiplication", test_string_multiplication)
    test("enumerate()", test_enumerate_builtin)
    test("zip()", test_zip_builtin)
    test("isinstance()", test_isinstance_builtin)
    test("reversed()", test_reversed_builtin)
    test("any()/all()", test_any_all_builtins)
    test("Extra string methods", test_extra_string_methods)

    # Example files
    _out("\n--- Example File Tests ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    example_files = ["hello.petal", "fizzbuzz.petal", "fibonacci.petal",
                     "data_structures.petal", "edge_cases.petal"]
    for fname in example_files:
        fpath = os.path.join(script_dir, fname)
        if os.path.exists(fpath):
            test(f"Example: {fname}", lambda fp=fpath: test_example_file(fp))

    # Phase 2: Web Framework
    _out("\n--- SEO Engine Tests ---")
    test("SEO import", test_seo_import)
    test("SEO meta tags", test_seo_meta_tags)
    test("SEO JSON-LD", test_seo_jsonld)
    test("SEO sitemap", test_seo_sitemap)
    test("SEO robots.txt", test_seo_robots)

    _out("\n--- Web Framework Tests ---")
    test("Web framework import", test_web_import)
    test("Template variable rendering", test_template_variable)
    test("Template for loop", test_template_for_loop)
    test("Template if/else", test_template_if_else)
    test("Template dot-access", test_template_dot_access)
    test("Component parsing", test_component_parsing)
    test("File-based router", test_router)
    test("CLI import", test_cli_import)
    
    _out("\n--- Full-Stack Backend Tests ---")
    test("env builtin variable loading", test_env_builtin)
    test("fetch builtin network mocking", test_fetch_builtin)
    test("API routes mapping & execution", test_api_routes)
    test("SSR page dynamic execution", test_ssr_page)

    # Phase 3: Full Build
    _out("\n--- Full Site Build Test ---")
    test("Full site build", test_full_site_build)

    # Summary
    passed = sum(1 for s, _ in results if s == "PASS")
    failed = sum(1 for s, _ in results if s == "FAIL")
    total = len(results)
    _out(f"\n{'=' * 60}")
    _out(f"RESULTS: {passed}/{total} passed, {failed} failed")
    _out(f"{'=' * 60}")

    if failed > 0:
        _out("\nFailed tests:")
        for status, name in results:
            if status == "FAIL":
                _out(f"  - {name}")

    # Write output to file (Windows encoding workaround)
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.txt")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    # Also try printing
    for line in output_lines:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", "replace").decode("ascii"))

    return failed == 0


class AssertionError(Exception):
    pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
