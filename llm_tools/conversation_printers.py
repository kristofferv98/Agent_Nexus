import random
import time
import threading

# Add this at the top of the file after imports
_lock = threading.Lock()
_last_print_time = 0
_min_print_gap = 0.002  # 2ms minimum gap between prints

def print_tool_call(tool_name: str, arguments: dict, result: str):
    """
    Prints a nicely formatted output whenever a tool is called as to show the tool call and result.
    
    Args:
        tool_name: Name of the tool that was called.
        arguments: A dictionary of arguments passed to the tool.
        result: The result or outcome from the tool.
    """
    # ANSI color codes
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Ensure minimum time gap between prints
    global _last_print_time
    with _lock:
        current_time = time.time()
        if _last_print_time > 0:
            time_since_last = current_time - _last_print_time
            if time_since_last < _min_print_gap:
                time.sleep(_min_print_gap - time_since_last)
        _last_print_time = time.time()
    
    def get_display_length(s: str) -> int:
        """Calculate display length accounting for emoji width"""
        emoji_width = {
            '🔧': 3,  # wrench
            '📝': 3,  # memo
            '📊': 3,  # chart
            '•': 2,   # bullet
        }
        
        # Check if string contains any emoji
        has_emoji = any(emoji in s for emoji in emoji_width)
        
        # Remove ANSI color codes for length calculation
        s_clean = s
        for color in [BLUE, GREEN, YELLOW, RESET, BOLD]:
            s_clean = s_clean.replace(color, '')
        
        length = 0
        i = 0
        while i < len(s_clean):
            for emoji, width in emoji_width.items():
                if s_clean.startswith(emoji, i):
                    length += width
                    i += len(emoji)
                    break
            else:
                length += 1
                i += 1
                
        # Add 1 to length if no emoji present
        if not has_emoji:
            length += 1
            
        return length

    # Calculate width based on content
    content_lines = [f"🔧 TOOL CALLED: {BLUE}{tool_name}{RESET}", f"📝 ARGUMENTS:"]
    for key, value in arguments.items():
        content_lines.append(f"• {YELLOW}{key}{RESET}: {value}")
    content_lines.append("📊 RESULT:")
    if result.strip():
        # Split long result lines to stay within width limit
        for line in result.splitlines():
            while get_display_length(line) > 90:  # 90 to account for padding
                split_point = 80
                while split_point > 0 and line[split_point] != ' ':
                    split_point -= 1
                if split_point == 0:
                    split_point = 80
                content_lines.append(f"{GREEN}{line[:split_point]}{RESET}")
                line = line[split_point:].strip()
            if line:
                content_lines.append(f"{GREEN}{line}{RESET}")
    
    # Set fixed width
    width = 96  # Setting to 96 to account for box characters and minimal padding
    
    def print_line(content=""):
        """Print a line with proper padding accounting for emoji width"""
        display_length = get_display_length(content)
        padding = width - display_length
        print(f"│ {content}{' ' * padding}│")
    
    # Box drawing characters with bold
    h_line = "─" * width
    box_style = BOLD
    
    # Print the box
    print(f"\n{box_style}┌{h_line}┐{RESET}")
    print_line(f"🔧 {BLUE}TOOL CALLED: {tool_name}{RESET}")
    print(f"{box_style}├{h_line}┤{RESET}")
    print_line(f"📝 ARGUMENTS:")
    for key, value in arguments.items():
        print_line(f"• {YELLOW}{key}{RESET}: {value}")
    print(f"{box_style}├{h_line}┤{RESET}")
    print_line(f"📊 RESULT:")
    if result.strip():
        for line in result.splitlines():
            print_line(f"{GREEN}{line}{RESET}")
    else:
        print_line(f"{GREEN}None{RESET}")
    print(f"{box_style}└{h_line}┘{RESET}\n")


def print_role_response(user_message: str, type: str = "agent"):
    """
    Prints a nicely formatted output for different role responses (agent/user).
    
    Args:
        user_message: The message to be displayed.
        type: The type of message ("agent" or "user").
    """
    # ANSI color codes
    PURPLE = '\033[95m'    # For agent text
    RED = '\033[91m'       # For agent box
    GREEN = '\033[92m'     # For user box
    WHITE = '\033[97m'     # For message text
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def get_display_length(s: str) -> int:
        """Calculate display length accounting for emoji width"""
        emoji_width = {
            '🤖': 3,  # robot for agent
            '👤': 3,  # user
            '•': 2,   # bullet
        }
        
        # Check if string contains any emoji
        has_emoji = any(emoji in s for emoji in emoji_width)
        
        # Remove ANSI color codes for length calculation
        s_clean = s
        for color in [PURPLE, RED, GREEN, WHITE, RESET, BOLD]:
            s_clean = s_clean.replace(color, '')
        
        length = 0
        i = 0
        while i < len(s_clean):
            for emoji, width in emoji_width.items():
                if s_clean.startswith(emoji, i):
                    length += width
                    i += len(emoji)
                    break
            else:
                length += 1
                i += 1
                
        # Add 1 to length if no emoji present
        if not has_emoji:
            length += 1
            
        return length
    
    # Set fixed width
    width = 96  # Setting to 96 to account for box characters and minimal padding
    
    # Set style based on type
    if type.lower() == "agent":
        emoji = "🤖"
        box_color = RED
        header = "AGENT RESPONSE:"
    else:
        emoji = "👤"
        box_color = GREEN
        header = "USER MESSAGE:"
    
    # Process message lines to stay within width limit
    content_lines = [f"{emoji} {WHITE}{header}{RESET}"]
    for line in user_message.splitlines():
        while get_display_length(f"{WHITE}{line}{RESET}") > 90:  # 90 to account for padding
            split_point = 80
            while split_point > 0 and line[split_point] != ' ':
                split_point -= 1
            if split_point == 0:
                split_point = 80
            content_lines.append(f"{WHITE}{line[:split_point]}{RESET}")
            line = line[split_point:].strip()
        if line:
            content_lines.append(f"{WHITE}{line}{RESET}")
    
    def print_line(content=""):
        """Print a line with proper padding accounting for emoji width"""
        display_length = get_display_length(content)
        padding = width - display_length
        print(f"{box_color}│{RESET} {content}{' ' * padding}{box_color}│{RESET}")
    
    # Box drawing characters with bold
    h_line = "─" * width
    box_style = BOLD
    
    # Print the box
    print(f"\n{box_style}{box_color}┌{h_line}┐{RESET}")
    print_line(f"{emoji} {WHITE}{header}{RESET}")
    print(f"{box_style}{box_color}├{h_line}┤{RESET}")
    for line in content_lines[1:]:  # Skip the header line as we've already printed it
        print_line(line)
    print(f"{box_style}{box_color}└{h_line}┘{RESET}\n")
