# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "inflection>=0.5.1,<0.6.0",
# ]
# ///

from __future__ import annotations

import keyword
import os
import shutil
import urllib3
from pathlib import Path
from typing import Any
import inflection


def openapi_url(ref: str) -> str:
    """Build OpenAPI spec URL from git ref."""
    return (
        "https://raw.githubusercontent.com/timonrieger/immich/"
        f"{ref}/open-api/immich-openapi-specs.json"
    )


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    # first get the underscore in, then take out all parenthesis with dashes, then underscore again
    snake = inflection.underscore(name)
    return inflection.parameterize(snake, separator="_")


def to_kebab_case(name: str) -> str:
    """Convert string to kebab-case."""
    snake = to_snake_case(name)
    return inflection.dasherize(snake)


def to_python_ident(name: str) -> str:
    """Convert an OpenAPI name into a safe Python identifier.

    This must match (or be compatible with) openapi-generator's Python naming:
    - snake_case
    - avoid keywords like `for`, `from`, `class`, etc.
    """
    ident = to_snake_case(name)
    if keyword.iskeyword(ident):
        ident = ident + "_"
    return ident


def python_type_from_schema(
    schema: dict[str, Any],
    spec: dict[str, Any] | None = None,
) -> str:
    """Convert OpenAPI schema to Python type hint."""
    # Extract enum name from $ref BEFORE normalization
    enum_name: str | None = None
    if "$ref" in schema:
        enum_name = schema["$ref"].split("/")[-1]

    nschema = normalize_schema(schema, spec)

    if "enum" in nschema:
        # Return enum name if we extracted it from $ref, otherwise fall back to str
        return enum_name if enum_name else "str"

    schema_type = nschema.get("type")
    if schema_type is None:
        return "str"
    if schema_type == "string":
        if "format" in nschema:
            fmt = nschema["format"]
            if fmt == "uuid":
                return "str"  # UUID as string for CLI
            if fmt == "date-time":
                return "datetime"  # Typer handles datetime parsing
        return "str"
    elif schema_type == "integer":
        return "int"
    elif schema_type == "number":
        return "float"
    elif schema_type == "boolean":
        return "bool"
    elif schema_type == "array":
        items = nschema.get("items", {})
        item_type = python_type_from_schema(items, spec)
        return f"list[{item_type}]"
    elif schema_type == "object":
        # Click can't map arbitrary objects; accept JSON as a string.
        return "str"


def resolve_schema_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a local OpenAPI $ref like '#/components/schemas/Foo'."""
    cur: Any = spec
    for part in ref.lstrip("#/").split("/"):
        cur = cur[part]
    return cur


def normalize_schema(
    schema: dict[str, Any], spec: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Normalize a schema for CLI generation.

    Today this focuses on "allOf" by merging object-ish schemas so we can keep
    generating dotted flags instead of collapsing to JSON strings.
    """
    # If we can, resolve refs up-front to expose actual types/properties.
    if "$ref" in schema and spec is not None:
        schema = resolve_schema_ref(spec, schema["$ref"])

    # Merge allOf when possible (common in Immich OpenAPI for composed DTOs).
    if "allOf" in schema and isinstance(schema.get("allOf"), list):
        merged: dict[str, Any] = {k: v for k, v in schema.items() if k != "allOf"}

        for sub in schema.get("allOf", []) or []:
            sub_norm = normalize_schema(sub, spec)
            for k, v in sub_norm.items():
                merged[k] = v

        schema = merged

    return schema


def is_complex_type(schema: dict[str, Any], spec: dict[str, Any] | None = None) -> bool:
    """Check if schema represents a complex type (object, array-of-object, oneOf/anyOf, etc.)."""
    schema = normalize_schema(schema, spec)

    schema_type = schema.get("type")
    if schema_type == "object":
        return True
    if schema_type == "array":
        items = schema.get("items", {})
        if "$ref" in items:
            # Resolve the ref to check if it's an enum/primitive or an object
            if spec is not None:
                resolved = resolve_schema_ref(spec, items["$ref"])
                # Enums and primitives are not complex - only objects are
                if "enum" in resolved:
                    return False  # Array of enums is simple
                # If it's an object or unknown, treat as complex
                return True
        return is_complex_type(items, spec)

    # oneOf, anyOf, allOf are complex
    if any(key in schema for key in ["oneOf", "anyOf", "allOf"]):
        return True

    return False


def flatten_schema(
    schema: dict[str, Any],
    spec: dict[str, Any],
    path: list[str] | None = None,
    required_path: bool = True,
) -> list[tuple[list[str], dict[str, Any], bool]]:
    """Flatten a schema into leaf entries with dotted paths.

    Returns list of (path_parts, schema, is_required) tuples.
    """
    if path is None:
        path = []

    schema = normalize_schema(schema, spec)

    schema_type = schema.get("type")

    # Primitive or enum - leaf node
    if schema_type in ("string", "integer", "number", "boolean") or "enum" in schema:
        return [(path, schema, required_path)]

    # Array of primitives - leaf node
    if schema_type == "array":
        items = schema.get("items", {})
        if not is_complex_type(items, spec):
            return [(path, schema, required_path)]
        # Array of objects - treat as complex
        return [(path, schema, required_path)]

    # Object - recurse into properties
    if schema_type == "object":
        props = schema.get("properties", {})
        if not props:
            # Empty object or additionalProperties - treat as complex
            return [(path, schema, required_path)]

        required_props = set(schema.get("required", []) or [])
        results: list[tuple[list[str], dict[str, Any], bool]] = []

        for prop_name, prop_schema in props.items():
            new_path = path + [prop_name]
            results.extend(
                flatten_schema(
                    prop_schema,
                    spec,
                    new_path,
                    required_path=(required_path and prop_name in required_props),
                )
            )

        return results


def option_name_for_path(path_parts: list[str]) -> str:
    """Generate dotted option name from path parts, e.g. ['user', 'name'] -> '--user.name'."""
    return "--" + ".".join(path_parts)


def python_triple_quoted_str(value: str) -> str:
    """Return a Python triple-quoted string literal for generated source code."""
    # Avoid accidental termination of the literal.
    safe = value.replace('"""', '\\"""')
    return f'"""{safe}"""'


def get_request_body_info(
    operation: dict[str, Any], spec: dict[str, Any]
) -> tuple[str, str, dict[str, Any], bool] | None:
    """Return (content_type, model_name, resolved_schema, is_required) for requestBody."""
    if "requestBody" not in operation:
        return None

    request_body = operation["requestBody"]
    is_required = request_body.get("required", False)
    content = request_body.get("content", {})
    if "application/json" in content:
        schema = content.get("application/json", {}).get("schema", {})
        ref = schema["$ref"]
        return (
            "application/json",
            ref.split("/")[-1],
            resolve_schema_ref(spec, ref),
            is_required,
        )
    if "multipart/form-data" in content:
        schema = content.get("multipart/form-data", {}).get("schema", {})
        ref = schema["$ref"]
        return (
            "multipart/form-data",
            ref.split("/")[-1],
            resolve_schema_ref(spec, ref),
            is_required,
        )


def generate_command_function(
    operation: dict[str, Any],
    spec: dict[str, Any],
    tag_attr: str,
    tag: str,
) -> str:
    """Generate a Typer command function for an operation.

    Returns:
        Generated function code as a string
    """
    operation_id = operation["operationId"]
    func_name = to_snake_case(operation_id)
    cmd_name = to_kebab_case(operation_id)

    # Extract and process parameters
    param_data: list[tuple[dict[str, Any], str]] = []  # (param, location)
    for param in operation.get("parameters", []):
        param_in = param["in"]
        if param_in in ("path", "query", "header"):
            param_data.append((param, param_in))

    # Get request body info
    request_body_info = get_request_body_info(operation, spec)

    # Build function signature
    lines = [f'@app.command("{cmd_name}")']
    lines.append(f"def {func_name}(")
    lines.append("    ctx: typer.Context,")

    # Track Python argument names to avoid duplicate arguments in the generated
    # function signature (e.g. path param `id` colliding with body field `id`).
    used_param_names: set[str] = {"ctx"}
    # Track all option names for collision detection
    used_option_names: set[str] = set()
    # Track boolean query params for conversion
    boolean_query_params: set[str] = set()

    # Process all parameters (path, query, header)
    processed_params: list[tuple[dict[str, Any], str, str, str, str, bool, bool]] = []
    # (param, location, param_name, param_type, flag_name, required, is_boolean_query)

    for param, location in sorted(
        param_data, key=lambda x: (x[1] != "path", x[0]["name"])
    ):
        openapi_name = param["name"]
        param_name = to_python_ident(openapi_name)
        used_param_names.add(param_name)
        schema = param.get("schema", {"type": "string"})
        required = param.get("required", False)
        description = param.get("description", "")
        flag_name = to_kebab_case(openapi_name)
        full_opt_name = f"--{flag_name}"
        is_boolean_query = False

        if location == "path":
            # Path parameters (required positional)
            param_type = python_type_from_schema(schema, spec)
            if required:
                lines.append(f"    {param_name}: {param_type},")
        else:
            # Query and header parameters (optional flags)
            used_option_names.add(full_opt_name)

            if location == "query":
                # Convert boolean query params to str to allow explicit true/false values
                # This matches server behavior where shared=true, shared=false, and undefined are distinct
                schema_type = schema.get("type")
                if schema_type == "boolean":
                    param_type = "str"
                    is_boolean_query = True
                    boolean_query_params.add(param_name)
                else:
                    param_type = python_type_from_schema(schema, spec)
            else:  # header
                param_type = python_type_from_schema(schema, spec)

            # Extract min/max constraints if available
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")

            # Generate Typer option
            if description:
                description_str = python_triple_quoted_str(description)
                help_arg = f", help={description_str}"
            else:
                help_arg = ""

            # Build min/max arguments
            min_arg = f", min={minimum}" if minimum is not None else ""
            max_arg = f", max={maximum}" if maximum is not None else ""

            # Define type with optional None based on required
            type_str = param_type if required else f"{param_type} | None"
            default_value = "..." if required else "None"
            lines.append(
                f'    {param_name}: {type_str} = typer.Option({default_value}, "--{flag_name}"{help_arg}{min_arg}{max_arg}),'
            )

        processed_params.append(
            (
                param,
                location,
                param_name,
                param_type,
                flag_name,
                required,
                is_boolean_query,
            )
        )

    # Request body options
    body_flags: list[
        tuple[list[str], dict[str, Any], bool, str, str]
    ] = []  # (path, schema, required, param_name, opt_name)

    if request_body_info:
        content_type, request_body_model, resolved_schema, body_required = (
            request_body_info
        )
        if content_type == "application/json":
            # Flatten schema and generate dotted flags
            flattened = flatten_schema(resolved_schema, spec)
            for path_parts, leaf_schema, is_required in flattened:
                opt_name = option_name_for_path(path_parts)
                used_option_names.add(opt_name)

                # Generate Python parameter name from path
                base_param_name = "_".join(to_python_ident(part) for part in path_parts)
                param_name = base_param_name

                # Avoid collisions with existing signature args (e.g. `id`)
                if param_name in used_param_names:
                    param_name = f"body_{param_name}"

                used_param_names.add(param_name)

                # Determine type
                # leaf_schema is already resolved in flatten_schema, so pass spec=None
                # to avoid re-resolving and handle schemas without explicit type
                param_type = python_type_from_schema(
                    leaf_schema,
                    spec=None,
                )
                is_complex = is_complex_type(leaf_schema, spec)
                description = leaf_schema.get("description", "")

                # Extract min/max constraints if available
                minimum = leaf_schema.get("minimum")
                maximum = leaf_schema.get("maximum")

                body_flags.append(
                    (path_parts, leaf_schema, is_required, param_name, opt_name)
                )

                # Emit Typer option
                # Construct description with example and complex help
                example = leaf_schema.get("example")
                description_parts = [description] if description else []

                if example is not None:
                    description_parts.append(f"Example: {example}")

                if is_complex:
                    description_parts.append(
                        f"Example: --{param_name} key1=value1,key2=value2"
                    )

                description = (
                    "\n\n".join(description_parts) if description_parts else ""
                )
                description_str = (
                    python_triple_quoted_str(description) if description else ""
                )

                # Define type with optional None
                type_str = param_type if is_required else f"{param_type} | None"
                default_value = "..." if is_required else "None"
                help_arg = f", help={description_str}" if description_str else ""

                # Build min/max arguments
                min_arg = f", min={minimum}" if minimum is not None else ""
                max_arg = f", max={maximum}" if maximum is not None else ""

                lines.append(
                    f'    {param_name}: {type_str} = typer.Option({default_value}, "{opt_name}"{help_arg}{min_arg}{max_arg}),'
                )
        elif content_type == "multipart/form-data":
            # Add file-part options for binary fields
            props = (
                resolved_schema.get("properties", {})
                if isinstance(resolved_schema, dict)
                else {}
            )
            required_props = set(resolved_schema.get("required", []) or [])
            for prop_name, prop_schema in sorted(props.items(), key=lambda kv: kv[0]):
                if (
                    prop_schema.get("type") == "string"
                    and prop_schema.get("format") == "binary"
                ):
                    arg_name = to_python_ident(prop_name)
                    opt_name = to_kebab_case(prop_name)
                    full_opt_name = f"--{opt_name}"
                    description = prop_schema.get("description", "")

                    used_option_names.add(full_opt_name)

                    if prop_name in required_props:
                        lines.append(
                            f'    {arg_name}: Path = typer.Option(..., "--{opt_name}", help="File to upload for {prop_name}"),'
                        )
                    else:
                        lines.append(
                            f'    {arg_name}: Path | None = typer.Option(None, "--{opt_name}", help="File to upload for {prop_name}"),'
                        )

    lines.append(") -> None:")

    # Function body
    summary = operation.get("summary", operation_id)
    doc_url = f"https://api.immich.app/endpoints/{inflection.parameterize(tag)}/{operation_id}"
    lines.append(f'    """{summary}\n\nDocs: {doc_url}\n    """')

    # Build kwargs
    lines.append("    kwargs = {}")

    # Add all params to kwargs
    for (
        param,
        location,
        param_name,
        param_type,
        flag_name,
        required,
        is_boolean_query,
    ) in processed_params:
        if location == "path":
            # Path params are always required and added directly
            lines.append(f"    kwargs['{param_name}'] = {param_name}")
        elif location == "query":
            # Convert boolean query params from string "true"/"false" to actual booleans
            if is_boolean_query:
                lines.append(f"    if {param_name} is not None:")
                lines.append(
                    f"        kwargs['{param_name}'] = {param_name}.lower() == 'true'"
                )
            else:
                if required:
                    lines.append(f"    kwargs['{param_name}'] = {param_name}")
                else:
                    lines.append(f"    if {param_name} is not None:")
                    lines.append(f"        kwargs['{param_name}'] = {param_name}")
        else:  # header
            # Header params are always optional
            lines.append(f"    if {param_name} is not None:")
            lines.append(f"        kwargs['{param_name}'] = {param_name}")

    # Handle request body
    if request_body_info:
        content_type, request_body_model, resolved_schema, body_required = (
            request_body_info
        )
        if content_type == "application/json":
            body_param_name = to_python_ident(request_body_model)
            model_module = to_snake_case(request_body_model)

            # Handle dotted flags path
            if body_flags:
                body_flag_params = [param_name for _, _, _, param_name, _ in body_flags]
                # Check if body is required but not provided
                if body_required:
                    lines.append(
                        f"    has_flags = any([{', '.join(body_flag_params)}])"
                    )
                    lines.append("    if not has_flags:")
                    lines.append(
                        '        raise SystemExit("Error: Request body is required. Use dotted body flags.")'
                    )
                lines.append("    if any([" + ", ".join(body_flag_params) + "]):")
                lines.append("        json_data = {}")

                for (
                    path_parts,
                    leaf_schema,
                    is_required,
                    param_name,
                    opt_name,
                ) in body_flags:
                    is_complex = is_complex_type(leaf_schema, spec)
                    value_expr = param_name

                    if is_required:
                        if is_complex:
                            lines.append(
                                f"        value_{param_name} = parse_complex_list({param_name})"
                            )
                            lines.append(
                                f"        set_nested(json_data, {path_parts!r}, value_{param_name})"
                            )
                        else:
                            lines.append(
                                f"        set_nested(json_data, {path_parts!r}, {value_expr})"
                            )
                    else:
                        lines.append(f"        if {param_name} is not None:")
                        if is_complex:
                            lines.append(
                                f"            value_{param_name} = parse_complex_list({param_name})"
                            )
                            lines.append(
                                f"            set_nested(json_data, {path_parts!r}, value_{param_name})"
                            )
                        else:
                            lines.append(
                                f"            set_nested(json_data, {path_parts!r}, {value_expr})"
                            )

                # Validate and create model
                lines.append(
                    f"        from immich.client.models.{model_module} import {request_body_model}"
                )
                lines.append(
                    f"        {body_param_name} = deserialize_request_body(json_data, {request_body_model})"
                )
                lines.append(f"        kwargs['{body_param_name}'] = {body_param_name}")
        elif content_type == "multipart/form-data":
            props = (
                resolved_schema.get("properties", {})
                if isinstance(resolved_schema, dict)
                else {}
            )
            required_props = set(resolved_schema.get("required", []) or [])
            lines.append("    json_data = {}  # noqa: F841")
            lines.append("    missing: list[str] = []")
            for prop_name, prop_schema in sorted(props.items(), key=lambda kv: kv[0]):
                snake = to_python_ident(prop_name)
                is_binary = (
                    prop_schema.get("type") == "string"
                    and prop_schema.get("format") == "binary"
                )
                if is_binary:
                    # File fields come from dedicated CLI options
                    if prop_name in required_props:
                        lines.append(
                            f"    kwargs['{snake}'] = load_file_bytes({snake})"
                        )
                    else:
                        lines.append(f"    if {snake} is not None:")
                        lines.append(
                            f"        kwargs['{snake}'] = load_file_bytes({snake})"
                        )
                else:
                    # Prefer original OpenAPI key, fallback to snake_case key
                    lines.append(f"    if '{prop_name}' in json_data:")
                    lines.append(
                        f"        kwargs['{snake}'] = json_data['{prop_name}']"
                    )
                    lines.append(f"    elif '{snake}' in json_data:")
                    lines.append(f"        kwargs['{snake}'] = json_data['{snake}']")
                    if prop_name in required_props:
                        lines.append("    else:")
                        lines.append(f"        missing.append('{prop_name}')")
            lines.append("    if missing:")
            lines.append(
                "        raise SystemExit("
                "\"Error: missing required multipart fields: \" + ', '.join(missing) + "
                '". Provide them via file options."'
                ")"
            )

    # Get client and API group
    lines.append("    client = ctx.obj['client']")

    # Call method
    method_name = to_snake_case(operation_id)
    lines.append(
        f"    result = run_command(client, client.{tag_attr}, '{method_name}', **kwargs)"
    )

    # Print result
    lines.append("    format_mode = ctx.obj.get('format', 'pretty')")
    lines.append("    print_response(result, format_mode)")

    return "\n".join(lines)


def generate_tag_app(
    tag: str, operations: list[tuple[str, str, dict[str, Any]]], spec: dict[str, Any]
) -> str:
    """Generate a Typer app module for a tag."""
    tag_attr = to_snake_case(tag)
    tag_description = next(t for t in spec["tags"] if t["name"] == tag)["description"]
    tag_slug = inflection.parameterize(tag)
    tag_help = f"{tag_description}\n\nDocs: https://api.immich.app/endpoints/{tag_slug}"

    lines = [
        '"""Generated CLI commands for '
        + tag
        + ' tag (auto-generated, do not edit)."""',
        "",
        "from __future__ import annotations",
        "",
        "from datetime import datetime",
        "from pathlib import Path",
        "import typer",
        "",
        "from immich.cli.runtime import load_file_bytes, deserialize_request_body, parse_complex_list, print_response, run_command, set_nested",
        "from immich.client.models import *",
        "",
    ]

    # Generate command for each operation
    command_codes: list[str] = []
    for path, method, operation in sorted(
        operations, key=lambda x: x[2].get("operationId", "")
    ):
        func_code = generate_command_function(operation, spec, tag_attr, tag)
        command_codes.append(func_code)

    lines.append(
        f"app = typer.Typer(help={python_triple_quoted_str(tag_help)}, context_settings={{'help_option_names': ['-h', '--help']}})"
    )
    lines.append("")

    # Add command functions
    for func_code in command_codes:
        lines.append(func_code)
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main codegen entrypoint."""
    commands_dir = Path(__file__).resolve().parents[2] / "immich" / "cli" / "commands"

    # Fetch OpenAPI spec
    url = openapi_url(os.environ.get("IMMICH_OPENAPI_REF", "main"))
    print(f"Fetching OpenAPI spec from: {url}")

    spec = urllib3.request("GET", url).json()

    # Validate and group operations
    operations_by_tag: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}

    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "patch", "delete"]:
                continue

            # Group by first tag
            tags = operation.get("tags", [])
            tag = tags[0] if tags else "default"
            if tag not in operations_by_tag:
                operations_by_tag[tag] = []
            operations_by_tag[tag].append((path, method, operation))

    # Clean and recreate commands directory
    if commands_dir.exists():
        shutil.rmtree(commands_dir)
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Generate app modules
    for tag in sorted(operations_by_tag.keys()):
        operations = operations_by_tag[tag]
        tag_snake = to_snake_case(tag)
        app_content = generate_tag_app(tag, operations, spec)

        app_file = commands_dir / f"{tag_snake}.py"
        app_file.write_text(app_content, encoding="utf-8")

    print(f"Generated CLI commands for {len(operations_by_tag)} tags")


if __name__ == "__main__":
    raise SystemExit(main())
