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
    openai_client = OpenAIAPI(model_name="gpt-4o")

    # Use the handler
    llm_handler = LLMHandler(openai_client)
    llm_handler.register_functions(functions)
    llm_handler.set_tools(schemas["openai"])

    # Set system instructions (optional)
    llm_handler.set_system_prompt("You are a helpfull friendly assitant that has the ability to use tools to help you answer questions and solve problems.")
    
    # Send user message
    user_query = "If I travel 500 km at 100 km/h, how long will it take?"
    print_role_response(user_query, "user")
    response = llm_handler.send_user_message(user_query)
    print_role_response(response, "agent")

    user_query = "If I go 330 miles at 85 miles/hour departing at 9:00, what time will I arrive? And how long if i go 88 miles/hour?"
    print_role_response(user_query, "user")
    response = llm_handler.send_user_message(user_query)
    print_role_response(response, "agent")
