# main.py
import traceback
from tool_converter import ToolConverter
from llm_tools.llm_handler import LLMHandler
from llm_api.openai_api import OpenAIAPI
from llm_api.anthropic_api import AnthropicAPI
from llm_api.groq_api import GroqAPI
from llm_api.gemini_api import GeminiAPI
from functions.math_tools import subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number

if __name__ == "__main__":
    # Instantiate the ToolConverter
    converter = ToolConverter()
    functions = [subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number]
    schemas = converter.generate_schemas(functions)
    print(schemas)

    system_prompt = """You are a helpful assistant that can perform mathematical operations.
"""

    # Flag to choose which LLM to run:
    run_openai = True
    run_anthropic = True
    run_groq = True
    run_gemini = True

    CONFIRMATION_PRINT = True

    try:
        if run_gemini:
            print("--------------------------------")
            # Gemini test
            gemini_client = GeminiAPI(model_name="gemini-2.0-flash-exp", VERBOSE=False, CONFIRMATION_PRINT=CONFIRMATION_PRINT, tools_schema=schemas["gemini"])
            llm = LLMHandler(gemini_client)
            llm.register_functions(functions)
            llm.set_tools(schemas["gemini"])
            llm.set_system_prompt(system_prompt)

            print("Gemini start")
            response = llm.send_user_message(
                "We are testing the following functions: subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number. Call as many functions as you can. "
                "Make a presentation about some extremely hard mathematical problems. Your final response should show these results."
            )
            print("Gemini response:", response)

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Full error breakdown: {traceback.format_exc()}")

    try:
        if run_groq:
            print("--------------------------------")
            # Groq test
            groq_client = GroqAPI(model_name="llama-3.3-70b-specdec", VERBOSE=False, CONFIRMATION_PRINT=CONFIRMATION_PRINT)
            llm = LLMHandler(groq_client)
            llm.register_functions(functions)
            llm.set_tools(schemas["groq"])
            llm.set_system_prompt(system_prompt)
            response = llm.send_user_message(
                "start by testing some of the tools and report back your findings. You can choose the numbers you want to use. "
                "call some in parallel first. then call some in series to compile some good math problems that you will present. "
                "We are testing the following functions: subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number. "
                "Make a presentation about some extremely hard mathematical problems. Your final response should be this as then conversation will end."
            )
            print("Groq response:", response)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Full error breakdown: {traceback.format_exc()}")

    try:
        if run_openai:
            print("--------------------------------")
            # OpenAI test
            openai_client = OpenAIAPI(model_name="gpt-4o", VERBOSE=False, CONFIRMATION_PRINT=CONFIRMATION_PRINT)
            llm = LLMHandler(openai_client)
            llm.register_functions(functions)
            llm.set_tools(schemas["openai"])
            llm.set_system_prompt(system_prompt)
            print("OpenAI start")
            response = llm.send_user_message(
                "start by testing some of the tools and report back your findings. You can choose the numbers you want to use. "
                "call some in parallel first. then call some in series to compile some good math problems that you will present. "
                "We are testing the following functions: subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number. "
                "Make a presentation about some extremely hard mathematical problems. Your final response should be this as then conversation will end."
            )
            print("OpenAI response:", response)
            response = llm.send_user_message("explain what you did in 2 sentences") 
            print("OpenAI response:", response)
            response = llm.send_user_message("explain what you did in 5 sentences")
            print("OpenAI response:", response)
            print(llm.handler.messages)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Full error breakdown: {traceback.format_exc()}")

    try:
        if run_anthropic:
            print("--------------------------------")
            # Anthropic test
            anthropic_client = AnthropicAPI(model_name="claude-3-5-sonnet-20240620", VERBOSE=False, CONFIRMATION_PRINT=CONFIRMATION_PRINT)
            llm = LLMHandler(anthropic_client)
            llm.register_functions(functions)
            llm.set_tools(schemas["anthropic"])
            llm.set_system_prompt(system_prompt)
            print("Anthropic start")
            response = llm.send_user_message(
                "start by testing some of the tools and report back your findings. You can choose the numbers you want to use. "
                "call some in parallel first. then call some in series to compile some good math problems that you will present. "
                "We are testing the following functions: subtract_numbers, add_numbers, multiply_numbers, divide_numbers, square_number, cube_number. "
                "Make a presentation about some extremely hard mathematical problems. Your final response should be this as then conversation will end."
            )
            print("Anthropic response:", response)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Full error breakdown: {traceback.format_exc()}")