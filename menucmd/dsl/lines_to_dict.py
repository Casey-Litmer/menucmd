import re



def lines_to_dict(lines: list[str]) -> dict:
    """
    Generic recursive descent parser for DSL format.
    
    Grammar (indentation-based):
    - Lines ending with ':' are block headers (e.g., Menu:, Item:, Colors:, func:)
    - Other lines are key:value pairs
    - Indentation (multiples of 4 spaces) determines nesting depth
    - Comments (#) and blank lines are stripped
    
    Returns a generic nested dict where:
    - Block types are keys (e.g., 'Menu', 'Item', 'Colors')
    - Multiple blocks of same type become lists
    - Non-opinionated: no semantic assumptions about block types
    - Fully extensible: add new block types by just using 'BlockName:'
    
    Example output structure:
    {
        "Menu": [
            {
                "name": "Hub",
                "id": "main_menu",
                "Colors": {...},
                "ExitColors": {...},
                "Item": [
                    {"key": "e", "message": "Test", "func": ["func(args)", ...], "Colors": {...}},
                    {"key": "b", "message": "Another", ...}
                ]
            },
            {
                "name": "Lazy Eval",
                "id": "lazy_menu",
                ...
            }
        ]
    }
    """
    lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    if not lines:
        return {}
    result, _ = _parse_block(lines, 0, 0)
    return result


def _parse_block(lines: list[str], start_idx: int, expected_indent: int, last_block_name: str = '') -> tuple[dict, int]:
    """
    Recursively parse all lines at a given indent level.
    
    Returns:
        (dict of parsed content, next unprocessed line index)
    """
    block = {}
    n = start_idx
    
    while n < len(lines):
        line = lines[n]
        current_indent = _get_indent(line)
        stripped = line.strip()
        
        # Exit Scope
        if current_indent < expected_indent:
            return block, n
        
        # Over-Indent
        if current_indent > expected_indent:
            raise IndentationError(line)
        
        # Block header (any line ending with ':')
        if stripped.endswith(':'):
            block_name = stripped[:-1]

            # First block must be Menu
            if block_name != 'Menu' and n == 0:
                raise SyntaxError(f"{block_name} must be a descendent of Menu")
            
            # Menu Heirarchy rules
            error = False
            match block_name:
                case 'Menu':
                    error = last_block_name in { 'Colors', 'Item', 'ExitColors', 'Menu'}
                case 'Item':
                    error = last_block_name in { 'Colors', 'Item', 'ExitColors' } 
                case 'Colors':
                    error = last_block_name in { 'Colors', 'ExitColors' }
                case 'ExitColors':
                    error = last_block_name in { 'Colors', 'Item', 'ExitColors' }

            if error:
                raise SyntaxError(f"{block_name} cannot be a descendent of {last_block_name}.")

            # Go to next stack
            sub_block, n = _parse_block(lines, n + 1, expected_indent + 1, block_name)
            
            # Add allowed duplicate BLOCKS here
            if block_name in { "Menu", "Item" }:
                if not block_name in block:
                    block[block_name] = []
                block[block_name].append(sub_block)
            else:
                if not block_name in block:
                    block[block_name] = sub_block
                else:
                    raise AttributeError(f"Duplicate block: {block_name}")
        
        # Key:value pair
        elif ':' in stripped:
            key, value = _parse_kv_line(stripped, last_block_name)
            
            # Add allowed duplicate KEYS here
            if key in { "func" }:
                if not key in block:
                    block[key] = []
                block[key].append(value)
            else:
                if not key in block:
                    block[key] = value
                else:
                    raise AttributeError(f"Duplicate attribute: {key}")
            n += 1
        else:
            raise SyntaxError(f"Unrecognized format: \n{stripped}")

    return block, n


def check_quotes(key: str, val: str, block_name: str):
    """Enforce quotes for string values."""

    # Keys that are expected to be quoted
    quoted_keys = { 'exit_key', 'exit_message' } \
    | ({ 'key', 'message', 'empty_message' } if block_name in { "Item" } else set()) \
    | ({ 'name', 'empty_message', 'invalid_key' } if block_name in { "Menu" } else set())

    if key in quoted_keys:
        if not ((val.startswith('"') and val.endswith('"')) or
                (val.startswith("'") and val.endswith("'"))):
            raise TypeError(
                f"Value '{val}' must be a quoted string. "
                f'Try "{val}"'
            )


def _parse_kv_line(line: str, block_name: str) -> tuple[str, str]:
    """
    Parse a key:value line.
    
    Handles quoted strings (both single and double quotes).
    Returns (key, value) where value is unquoted if it was quoted.
    """
    #split_pattern = r"([^:]+):([^:]+.*)"
    match = re.match(r'([^:]+):\s*(.*)', line)
    if not match:
        raise ValueError(f"Invalid key:value syntax: {line}")
    
    key = match.group(1).strip()
    value = match.group(2).strip()
    
    # Enforce quoting conventions
    check_quotes(key, value, block_name)    
    
    return key, value


def _get_indent(line: str) -> int:
    """
    Get indentation level.

    Counts leading spaces and divides by 4 (1 level = 4 spaces).
    """
    if not line or not line[0].isspace():
        return 0
    spaces = len(line) - len(line.lstrip(' '))
    return spaces // 4