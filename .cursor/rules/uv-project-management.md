#### `.cursor/rules/uv-project-management.md`
```markdown
description: UV project management requirements for Python projects
globs: "**/pyproject.toml", "**/*.py"
priority: critical
category: project-management
alwaysApply: true
---

# UV Project Management Rules

## MANDATORY UV Usage
- **NO PIP**: Never use pip install, pip freeze, requirements.txt for new dependencies
- **UV ONLY**: All dependency management through uv add, uv remove, uv sync
- **pyproject.toml**: All configuration in pyproject.toml

## Required pyproject.toml Structure
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[project]
name = "your-project"
dependencies = [
    # Core dependencies with specific versions
    "pydicom>=2.3.0",
    "nibabel>=4.0.0", 
    "pandas>=1.5.0",
    "openpyxl>=3.1.0",  # Always include for Excel support
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.ruff]
line-length = 88
target-version = "py39"
```

## Development Workflow
```bash
# ✅ Correct workflow
uv sync --dev              # Install all dependencies
uv add new-package         # Add new dependency
uv run black src/          # Format code
uv run ruff check src/     # Check code quality
uv run mypy src/           # Type checking
uv run pytest             # Run tests
```

## ❌ NEVER DO
- pip install anything
- requirements.txt for new dependencies
- setup.py files
- conda for Python dependencies
```