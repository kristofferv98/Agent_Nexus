from llm_api.openai_api import OpenAIAPI
from tool_converter import ToolConverter
from llm_tools.llm_handler import LLMHandler
from typing import Optional
import math
import datetime

def print_tool_call(tool_name: str, arguments: dict, result: str):
    """
    Prints a nicely formatted output whenever a tool is called as to show the tool call and result. (does not work with parallel calls)
    
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

    # Calculate required width based on content
    content_lines = [f"🔧 TOOL CALLED: {BLUE}{tool_name}{RESET}", f"📝 ARGUMENTS:"]
    for key, value in arguments.items():
        content_lines.append(f"• {YELLOW}{key}{RESET}: {value}")
    content_lines.append("📊 RESULT:")
    if result.strip():
        content_lines.extend([f"{GREEN}{line}{RESET}" for line in result.splitlines()])
    
    # Calculate width based on longest line
    width = max(get_display_length(line) for line in content_lines)
    width = max(width + 4, 70)  # Add minimal padding and ensure minimum width
    
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

def convert_miles_to_km(miles: float) -> float:
    """
    Converts miles to kilometers.
    """
    print_tool_call("convert_miles_to_km", {"miles": miles}, f"{miles * 1.60934} km")
    return miles * 1.60934

def calculate_travel_time(distance_km: float, speed_kmh: float, start_time: Optional[str] = None) -> str:
    """
    Calculates travel time in hours, and provides departure time and arrival time
    based on a distance, speed, and an optional starting time.

    Args:
        distance_km: The distance of the travel in kilometers.
        speed_kmh: The speed of the travel in kilometers per hour.
        start_time: (Optional) The start time of the travel in format "HH:MM",
                    Calculated using the default timezone for the machine

    Returns:
        A string containing the calculated travel time, and estimated arrival
        time if the start time is provided, or a error message.
    """

    if speed_kmh <= 0:
        return "Speed must be a positive number."
    if distance_km < 0:
        return "Distance must be a non-negative number."

    travel_hours = distance_km / speed_kmh
    hours = math.floor(travel_hours)
    minutes = math.ceil((travel_hours - hours) * 60)

    result = f"The travel time is approximately {hours} hours and {minutes} minutes."

    if start_time:
        try:
            start_datetime = datetime.datetime.strptime(start_time, "%H:%M")
            arrival_datetime = start_datetime + datetime.timedelta(hours=hours, minutes=minutes)
            arrival_time = arrival_datetime.strftime("%H:%M")
            result += (
                f"\nDeparting at {start_time}, "
                f"the arrival time is estimated to be at: {arrival_time}."
            )
        except ValueError:
            return "Invalid start time format. Please use HH:MM for time."

    print_tool_call("calculate_travel_time", {"distance_km": distance_km, "speed_kmh": speed_kmh, "start_time": start_time}, result)
    return result



if __name__ == "__main__":
    converter = ToolConverter()
    # Include your custom function
    functions = [calculate_travel_time, convert_miles_to_km]  # Changed to new function

    # Generate schemas
    schemas = converter.generate_schemas(functions)

    # Create LLM client
    openai_client = OpenAIAPI(model_name="gpt-4o-mini")

    # Use the handler
    llm_handler = LLMHandler(openai_client)
    llm_handler.register_functions(functions)
    llm_handler.set_tools(schemas["openai"])

    # Set system instructions (optional)
    llm_handler.set_system_prompt("You are a helpfull assitant that use")

    # Send user message
    response = llm_handler.send_user_message("If I travel 500 km at 100 km/h, how long will it take?")
    print(f"\nLLM Response (openai):\n{response}\n")

    response = llm_handler.send_user_message("If I go 330 miles at 95 miles/hour departing at 9:00, what time will I arrive? ")
    print(f"\nLLM Response (openai):\n{response}\n")
