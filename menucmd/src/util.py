import sys
import shutil
import re



def count_visual_lines(text: str) -> int:
    """Calculates the number of visual lines a string will occupy in the terminal."""
    try:
        # Fallback for environments without a TTY (e.g., in certain test runners)
        width = shutil.get_terminal_size().columns
    except OSError:
        width = 80

    line_count = 0
    # Split the text into lines based on the newline character
    for line in text.split('\n'):
        # Strip ANSI escape codes for accurate length calculation
        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
        
        # An empty string from split() still represents a line (e.g., from `\n\n` or trailing `\n`)
        if not clean_line:
            line_count += 1
        else:
            # Ceiling division to calculate wrapped lines for non-empty lines
            line_count += (len(clean_line) + width - 1) // width

    return line_count


def clear_lines(printed_lines: int) -> None:
    """Clears previous menu from terminal"""
    if printed_lines <= 0:
        return
    for _ in range(printed_lines):
        sys.stdout.write("\x1b[1A\x1b[2K\r")
    sys.stdout.flush()