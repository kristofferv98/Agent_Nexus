from llm_api.openai_api import OpenAIAPI
from tool_converter import ToolConverter
from llm_tools.llm_handler import LLMHandler
from typing import Optional
import math
import datetime

from llm_tools.conversation_printers import print_tool_call, print_role_response

def convert_miles_to_km(miles: float) -> float:
    """
    Converts miles to kilometers.
    """
    print_tool_call("convert_miles_to_km", {"miles": miles}, f"{miles * 1.60934} km")
    return miles * 1.60934

def calculate_travel_time(distance_km: float, speed_kmh: float, start_time: Optional[str] = None) -> str:
    """
    Calculates travel time in days, hours, and minutes, and provides departure time and arrival time
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
    days = math.floor(travel_hours / 24)
    remaining_hours = travel_hours % 24
    hours = math.floor(remaining_hours)
    minutes = math.ceil((remaining_hours - hours) * 60)

    result = ""
    if days > 0:
        result += f"{days} days, "
    result += f"{hours} hours and {minutes} minutes"
    result = f"The travel time is approximately {result}."

    if start_time:
        try:
            start_datetime = datetime.datetime.strptime(start_time, "%H:%M")
            arrival_datetime = start_datetime + datetime.timedelta(days=days, hours=hours, minutes=minutes)
            arrival_time = arrival_datetime.strftime("%H:%M")
            result += (
                f"\nDeparting at {start_time}, "
                f"the arrival time is estimated to be at: {arrival_time}"
            )
            if days > 0:
                result += f" ({'+' + str(days) + ' days' if days == 1 else '+' + str(days) + ' days'})"
            result += "."
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
    openai_client = OpenAIAPI(model_name="gpt-4o")

    # Use the handler
    llm_handler = LLMHandler(openai_client)
    llm_handler.register_functions(functions)
    llm_handler.set_tools(schemas["openai"])

    # Set system instructions (optional)
    llm_handler.set_system_prompt("You are a helpfull friendly assitant christmas elf that has the ability to use tools to help you answer questions to the user. You are charefull and polite, since its now christmas time.")
    
    user_query = "Santa needs to deliver presents around the Earth's circumference (approximately 24,901 miles) at his magical sleigh speed of 2,000 miles per hour, leaving the North Pole at 00:00 on Christmas Eve. When will he complete his journey? And if the reindeers get tired halfway and can only operate at half speed for the rest of the journey, will he still make it?🎄✨"
    print_role_response(user_query, "user")
    response = llm_handler.send_user_message(user_query)
    print_role_response(response, "agent")
