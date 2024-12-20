import re
import time
import threading
from wcwidth import wcswidth

_lock = threading.Lock()
_last_print_time = 0
_min_print_gap = 0.002  # minimum gap between prints in seconds

def strip_ansi_codes(s: str) -> str:
    """Remove ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', s)

def get_display_width(s: str) -> int:
    """Return the display width of a string considering wide chars and emojis."""
    s_clean = strip_ansi_codes(s)
    width = wcswidth(s_clean)
    # wcswidth returns -1 if it encounters a non-printable/wide char it can't handle
    if width < 0:
        width = len(s_clean)  # Fallback: at least count characters if something is unusual
    return width

def ensure_min_time_gap():
    global _last_print_time
    with _lock:
        current_time = time.time()
        time_since_last = current_time - _last_print_time
        if _last_print_time > 0 and time_since_last < _min_print_gap:
            time.sleep(_min_print_gap - time_since_last)
        _last_print_time = time.time()


def print_tool_call(tool_name: str, arguments: dict, result: str):
    """
    Prints a nicely formatted output whenever a tool is called.
    """
    # ANSI color codes
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    ensure_min_time_gap()

    width = 96  # desired width of the box

    # Prepare lines
    content_lines = [
        f"🔧 TOOL CALLED: {BLUE}{tool_name}{RESET}",
        "📝 ARGUMENTS:"
    ]
    for key, value in arguments.items():
        content_lines.append(f"• {YELLOW}{key}{RESET}: {value}")
    content_lines.append("📊 RESULT:")

    # Split result lines if they are too long
    if result.strip():
        for line in result.splitlines():
            while get_display_width(line) > 90:
                # find a split point near 80 chars to keep lines neat
                split_point = 80
                # move split point to a nearest space if possible
                while split_point > 0 and split_point < len(line) and line[split_point] != ' ':
                    split_point -= 1
                if split_point == 0:
                    split_point = 80
                # append the first part
                content_lines.append(f"{GREEN}{line[:split_point]}{RESET}")
                # continue with the remainder
                line = line[split_point:].strip()
            if line:
                content_lines.append(f"{GREEN}{line}{RESET}")
    else:
        content_lines.append(f"{GREEN}None{RESET}")

    def print_line(content=""):
        display_length = get_display_width(content)
        padding = width - display_length - 1  # Changed to -1 to account for the single space after │
        print(f"│ {content}{' ' * padding}│")

    # Box drawing
    h_line = "─" * width
    print(f"\n{BOLD}┌{h_line}┐{RESET}")
    # print content lines
    for idx, line in enumerate(content_lines):
        print_line(line)
        # Add separators as needed
        if idx == 0 or idx == 1 + len(arguments):
            print(f"{BOLD}├{h_line}┤{RESET}")
    print(f"{BOLD}└{h_line}┘{RESET}\n")


def print_role_response(user_message: str, type: str = "agent"):
    """
    Prints a nicely formatted output for different role responses (agent/user).
    """
    # ANSI color codes
    PURPLE = '\033[95m'    # For agent text
    RED = '\033[91m'       # For agent box
    GREEN = '\033[92m'     # For user box
    WHITE = '\033[97m'     # For message text
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    width = 96

    if type.lower() == "agent":
        emoji = "🤖"
        box_color = RED
        header = "AGENT RESPONSE:"
    else:
        emoji = "👤"
        box_color = GREEN
        header = "USER MESSAGE:"

    # Split long lines
    content_lines = [f"{emoji} {WHITE}{header}{RESET}"]
    # Replace double newlines with a special marker
    message_lines = user_message.replace('\n\n', '\n<DOUBLE_BREAK>\n').splitlines()
    
    for line in message_lines:
        if line == '<DOUBLE_BREAK>':
            content_lines.append('')  # Add empty line for double breaks
            continue
        
        line_stripped = line
        # split if line is too long
        while get_display_width(line_stripped) > 90:
            split_point = 80
            while split_point > 0 and split_point < len(line_stripped) and line_stripped[split_point] != ' ':
                split_point -= 1
            if split_point == 0:
                split_point = 80
            content_lines.append(f"{WHITE}{line_stripped[:split_point]}{RESET}")
            line_stripped = line_stripped[split_point:].strip()
        if line_stripped:
            content_lines.append(f"{WHITE}{line_stripped}{RESET}")

    def print_line(content=""):
        display_length = get_display_width(content)
        padding = width - display_length - 1  # Changed to -1 to account for the single space after │
        print(f"{box_color}│{RESET} {content}{' ' * padding}{box_color}│{RESET}")

    h_line = "─" * width
    # Print the box
    ensure_min_time_gap()
    print(f"\n{BOLD}{box_color}┌{h_line}┐{RESET}")
    # print the header
    print_line(content_lines[0])
    print(f"{BOLD}{box_color}├{h_line}┤{RESET}")
    # print the message lines
    for line in content_lines[1:]:
        print_line(line)
    print(f"{BOLD}{box_color}└{h_line}┘{RESET}\n")
