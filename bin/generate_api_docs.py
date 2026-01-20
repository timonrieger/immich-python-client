#!/usr/bin/env python3
"""Generate API documentation markdown files from generated API classes."""

from pathlib import Path


def filename_to_title(filename: str) -> str:
    """Convert filename like 'activities_api.py' to 'Activities Api'."""
    # Remove .py extension
    name = filename.replace(".py", "")
    # Split by underscore
    parts = name.split("_")
    # Capitalize each part
    return " ".join(part.capitalize() for part in parts)


def filename_to_class_name(filename: str) -> str:
    """Convert filename like 'activities_api.py' to 'ActivitiesApi'."""
    # Remove .py extension
    name = filename.replace(".py", "")
    # Split by underscore, capitalize each part, and join
    parts = name.split("_")
    return "".join(part.capitalize() for part in parts)


def get_module_path(file_path: Path, project_root: Path) -> str:
    """Convert file path to Python module path."""
    # Get relative path from project root
    rel_path = file_path.relative_to(project_root)
    # Convert to module path (replace / with .)
    module_path = str(rel_path).replace("/", ".").replace(".py", "")
    return module_path


def generate_markdown_content(filename: str, module_path: str, class_name: str) -> str:
    """Generate markdown content for an API class."""
    title = filename_to_title(filename)

    content = f"""
# {title}

::: {module_path}.{class_name}
"""
    return content


def main():
    """Generate markdown files for all API classes."""
    # Paths
    project_root = Path(__file__).parent.parent
    api_dir = project_root / "immich" / "client" / "generated" / "api"
    docs_dir = project_root / "docs" / "client" / "reference"

    # Create docs/client directory if it doesn't exist
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Find all *_api.py files
    api_files = sorted(api_dir.glob("*_api.py"))

    if not api_files:
        print(f"No API files found in {api_dir}")
        return

    print(f"Found {len(api_files)} API files")

    # Generate markdown for each API file
    for api_file in api_files:
        filename = api_file.name
        class_name = filename_to_class_name(filename)
        module_path = get_module_path(api_file, project_root)

        # Generate markdown content
        content = generate_markdown_content(filename, module_path, class_name)

        # Write to docs/client/reference/{filename}.md
        output_file = docs_dir / filename.replace(".py", ".md")
        output_file.write_text(content)
        print(f"Generated: {output_file.relative_to(project_root)}")

    print(
        f"\nGenerated {len(api_files)} documentation files in {docs_dir.relative_to(project_root)}"
    )


if __name__ == "__main__":
    main()
