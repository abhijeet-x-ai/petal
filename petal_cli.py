#!/usr/bin/env python3
"""
Petal CLI -- Command-line tool for the Petal web framework.

Usage:
    python petal_cli.py new <project-name>    Create a new Petal website
    python petal_cli.py dev                   Start development server
    python petal_cli.py build                 Build for production
    python petal_cli.py preview               Preview the production build
    python petal_cli.py run <script.petal>     Run a Petal script
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


PETAL_VERSION = "0.1.0"

LOGO = """
    Petal v{version}
    The world's easiest web language
""".format(version=PETAL_VERSION)


def _safe_print(msg=""):
    """Print that handles Windows encoding gracefully."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def cmd_new(project_name):
    """Create a new Petal website project."""
    _safe_print(LOGO)
    _safe_print(f"  Creating new project: {project_name}\n")

    project_dir = Path(project_name)
    if project_dir.exists():
        _safe_print(f"  [!] Directory '{project_name}' already exists!")
        sys.exit(1)

    # Look for starter template
    petal_root = Path(os.path.dirname(os.path.abspath(__file__)))
    starter_dir = petal_root / "starter"

    if starter_dir.exists():
        # Copy starter template
        shutil.copytree(starter_dir, project_dir)
        _safe_print(f"  [OK] Project created from starter template")
    else:
        # Create minimal project structure
        _create_minimal_project(project_dir)
        _safe_print(f"  [OK] Project created with minimal template")

    _safe_print(f"\n  Next steps:")
    _safe_print(f"    cd {project_name}")
    _safe_print(f"    python {petal_root / 'petal_cli.py'} dev")
    _safe_print()


def _create_minimal_project(project_dir):
    """Create a minimal project when no starter template exists."""
    dirs = ["pages", "components", "layouts", "static"]
    for d in dirs:
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    # petal.config
    (project_dir / "petal.config").write_text(
        '# Petal Website Configuration\n'
        'site_name = "My Petal Website"\n'
        'site_url = "https://example.com"\n'
        'site_description = "Built with Petal"\n'
        'author = "Your Name"\n'
        'language = "en"\n'
        'layout = "Base"\n',
        encoding="utf-8"
    )

    # Basic layout
    (project_dir / "layouts" / "Base.petal").write_text(
        '---\n'
        '# Base layout\n'
        '---\n'
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="utf-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '    <link rel="stylesheet" href="/style.css">\n'
        '</head>\n'
        '<body>\n'
        '    {slot}\n'
        '</body>\n'
        '</html>\n',
        encoding="utf-8"
    )

    # Basic index page
    (project_dir / "pages" / "index.petal").write_text(
        '---\n'
        'title = "Welcome"\n'
        'description = "Welcome to my Petal website"\n'
        '---\n'
        '<h1>Welcome to Petal</h1>\n'
        '<p>Edit pages/index.petal to get started.</p>\n',
        encoding="utf-8"
    )

    # Basic CSS
    (project_dir / "static" / "style.css").write_text(
        'body {\n'
        '    font-family: system-ui, -apple-system, sans-serif;\n'
        '    max-width: 800px;\n'
        '    margin: 0 auto;\n'
        '    padding: 2rem;\n'
        '    color: #333;\n'
        '}\n',
        encoding="utf-8"
    )


def cmd_dev(port=3000):
    """Start the development server."""
    _safe_print(LOGO)
    from petal_web import DevServer

    project_dir = _find_project_dir()
    dev = DevServer(project_dir, port=port)
    dev.start()


def cmd_build():
    """Build the site for production."""
    _safe_print(LOGO)
    from petal_web import StaticSiteGenerator

    project_dir = _find_project_dir()
    ssg = StaticSiteGenerator(project_dir)
    ssg.build()


def cmd_preview(port=3001):
    """Preview the production build."""
    _safe_print(LOGO)
    from http.server import HTTPServer
    from petal_web import PetalFullStackHandler

    project_dir = Path(_find_project_dir())
    dist_dir = project_dir / "dist"

    if not dist_dir.exists():
        _safe_print("  [!] No dist/ directory found. Run 'petal build' first.")
        sys.exit(1)

    dist = str(dist_dir)
    project = str(project_dir)
    handler = lambda *args, **kwargs: PetalFullStackHandler(*args, project_dir=project, dist_dir=dist, **kwargs)
    server = HTTPServer(("localhost", port), handler)

    _safe_print(f"  Previewing production build:")
    _safe_print(f"  http://localhost:{port}")
    _safe_print(f"\n  Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _safe_print("\n  Preview stopped.")
        server.server_close()


def cmd_start(port=3000):
    """Start the production full-stack server (no file watching/auto-rebuild)."""
    _safe_print(LOGO)
    from http.server import HTTPServer
    from petal_web import PetalFullStackHandler

    project_dir = Path(_find_project_dir())
    dist_dir = project_dir / "dist"

    if not dist_dir.exists():
        _safe_print("  [!] No dist/ directory found. Run 'petal build' first.")
        sys.exit(1)

    dist = str(dist_dir)
    project = str(project_dir)
    handler = lambda *args, **kwargs: PetalFullStackHandler(*args, project_dir=project, dist_dir=dist, **kwargs)
    server = HTTPServer(("localhost", port), handler)

    _safe_print(f"  Starting Petal full-stack server:")
    _safe_print(f"  http://localhost:{port}")
    _safe_print(f"\n  Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _safe_print("\n  Server stopped.")
        server.server_close()


def cmd_run(script_path):
    """Run a Petal script file."""
    from petal import run_source, PetalError

    if not os.path.exists(script_path):
        _safe_print(f"  [!] File not found: {script_path}")
        sys.exit(1)

    with open(script_path, "r") as f:
        source = f.read()

    try:
        run_source(source)
    except PetalError as e:
        _safe_print(f"  Petal Error -- {e.format()}")
        sys.exit(1)


def _find_project_dir():
    """Find the project root (directory containing petal.config or pages/)."""
    cwd = Path.cwd()

    # Check current directory
    if (cwd / "petal.config").exists() or (cwd / "pages").exists():
        return str(cwd)

    # Check parent directories
    for parent in cwd.parents:
        if (parent / "petal.config").exists() or (parent / "pages").exists():
            return str(parent)

    # Default to current directory
    return str(cwd)


def main():
    """Main entry point for the CLI."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        _safe_print(LOGO)
        _safe_print("  Commands:")
        _safe_print("    new <name>        Create a new Petal website")
        _safe_print("    dev               Start development server")
        _safe_print("    build             Build for production (static HTML)")
        _safe_print("    preview           Preview the production build")
        _safe_print("    start             Start production full-stack server")
        _safe_print("    run <file.petal>  Run a Petal script")
        _safe_print()
        _safe_print("  Examples:")
        _safe_print("    python petal_cli.py new my-blog")
        _safe_print("    python petal_cli.py dev")
        _safe_print("    python petal_cli.py build")
        _safe_print("    python petal_cli.py start")
        _safe_print()
        sys.exit(0)

    command = args[0]

    if command == "new":
        if len(args) < 2:
            _safe_print("  [!] Please provide a project name: petal new <name>")
            sys.exit(1)
        cmd_new(args[1])

    elif command == "dev":
        port = int(args[1]) if len(args) > 1 else 3000
        cmd_dev(port)

    elif command == "build":
        cmd_build()

    elif command == "preview":
        port = int(args[1]) if len(args) > 1 else 3001
        cmd_preview(port)

    elif command == "start":
        port = int(args[1]) if len(args) > 1 else 3000
        cmd_start(port)

    elif command == "run":
        if len(args) < 2:
            _safe_print("  [!] Please provide a file: petal run <file.petal>")
            sys.exit(1)
        cmd_run(args[1])

    elif command == "--version":
        _safe_print(f"Petal v{PETAL_VERSION}")

    else:
        # Try to run as a script file
        if os.path.exists(command) and command.endswith(".petal"):
            cmd_run(command)
        else:
            _safe_print(f"  [!] Unknown command: {command}")
            _safe_print(f"     Run 'python petal_cli.py help' for usage.")
            sys.exit(1)


if __name__ == "__main__":
    main()
