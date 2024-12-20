# Multi-LLM Tool Integration Codebase

Welcome to this multi-LLM tool integration codebase! This repository provides a system that meets the following goals:

- Dynamically generates and transforms JSON schemas for Python functions (so that various Large Language Model (LLM) providers can read and call them).  
- Connects with multiple LLMs (OpenAI, Anthropic, Gemini, and Groq) through a uniform interface.  
- Transparently handles the logic of how messages, tool calls, and responses are processed.  

Below, you’ll find a high-level overview of each component, instructions on setting up and running the project, and tips for extending it with your own functions and logic.

---

## Table of Contents

1. [Overview of Key Components](#overview-of-key-components)  
2. [Directory Structure](#directory-structure)  
3. [Installation and Setup](#installation-and-setup)  
4. [Usage Guide](#usage-guide)  
   - [Generating JSON Schemas with ToolConverter](#generating-json-schemas-with-toolconverter)  
   - [Registering Functions with LLMHandler](#registering-functions-with-llmhandler)  
   - [Running the Main Script](#running-the-main-script)  
5. [Adding Your Own Tools / Functions](#adding-your-own-tools--functions)  
6. [Details of Each Module](#details-of-each-module)  
7. [Example Snippets](#example-snippets)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## Overview of Key Components

This project’s main functionality resides in bridging Python-based “tools” (i.e., functions) with various LLM APIs. To accomplish this, we have:

- **ToolConverter**: A utility class that dynamically converts Python functions into JSON schemas for OpenAI-style function calls, then adapts those schemas to Anthropic, Gemini, and Groq formats.  
- **LLMHandler**: A high-level orchestrator that sends messages to an LLM, handles tool calls, and returns the final text response to the user. It integrates with a chosen LLM client (OpenAI, Anthropic, Gemini, Groq) through a standard interface (the base API).  
- **LLM API Wrappers**: Each LLM vendor (OpenAI, Anthropic, Gemini, Groq) is wrapped in a dedicated module, conforming to a unified interface (defined in base_api.py).  
- **MessageHandler**: Manages message formatting, storing system/user/tool messages in a standardized structure.  

With these components, you can easily add your own Python functions (tools) that an LLM may call to perform tasks such as math calculations, file I/O, or anything else your application needs.

---

## Directory Structure

Here’s a simplified structure of the repository:

```
.
├── functions/
│   └── math_tools.py         # Example math functions (tools)
├── llm_api/
│   ├── base_api.py           # Abstract base interface for LLM API classes
│   ├── openai_api.py         # Wrapper for OpenAI
│   ├── anthropic_api.py      # Wrapper for Anthropic
│   ├── gemini_api.py         # Wrapper for Gemini
│   └── groq_api.py           # Wrapper for Groq
├── llm_tools/
│   ├── llm_handler.py        # Main orchestrator class for LLM usage
│   └── message_handler.py    # Handles message creation and formatting
├── tool_converter.py         # ToolConverter: generates JSON schemas
└── main.py                   # Example driver script that ties everything together
```

---

## Installation and Setup

1. Clone this repository:  
   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo
   ```

2. Create and activate a virtual environment (optional, but recommended):  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies (example using pip):  
   ```bash
   pip install -r requirements.txt
   ```

4. Set your environment variables for LLM provider credentials (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, GROQ_API_KEY).  

5. (Optional) If running on macOS with M2, you can ensure any specialized dependencies (like Rosetta, if needed) are properly configured.

---

## Usage Guide

### Generating JSON Schemas with ToolConverter

The ToolConverter takes in a list of Python functions and generates a schema that the LLM can use to understand arguments, parameter validation, and usage.

You’ll find an example in:
```python
class ToolConverter():
    ...
    def generate_schemas(self, functions: List[Callable]) -> dict:
        ...
```

When you provide a list of functions (e.g., [subtract_numbers, add_numbers, multiply_numbers]), it returns a dictionary containing OpenAI, Anthropic, Gemini, and Groq schemas for those functions.  

### Registering Functions with LLMHandler

The LLMHandler manages the conversation loop. Whenever the LLM attempts to call a tool, LLMHandler intercepts the request and calls the actual Python code.

For example, in:
```python
class LLMHandler:
    ...
    def register_functions(self, functions: List[Callable]):
        for func in functions:
            self.register_function(func)
    ...
```

By calling `register_functions([your_func_1, your_func_2])`, you make those tools available to any LLM you choose to integrate.

### Running the Main Script

An example usage is in “main.py”. It:

1. Initializes ToolConverter.  
2. Gathers your tools (e.g., math functions).  
3. Generates the schemas for all LLM flavors.  
4. Instantiates an LLM client (e.g., OpenAI) and an LLMHandler.  
5. Registers the tools and sets the system prompt.  
6. Sends user messages to the LLM, which can call the newly registered tools as needed.  

You can run:  
```bash
python main.py
```
Adjust the flags in the script (run_openai, run_anthropic, run_groq, run_gemini) to choose which LLM(s) to test.

---

## Adding Your Own Tools / Functions

1. Import or define new Python functions.  
2. Give them docstrings and type annotations (if possible) for clarity and better schema generation.  
3. Pass them to the `ToolConverter.generate_schemas()` method.  
4. Register them with your LLMHandler instance.  

For example, if you have:
```python
def greet_user(name: str) -> str:
    """Greets a user by name."""
    return f"Hello, {name}!"
```
Add it to the code flow in “main.py” (or another script) similarly to how math_tools are used.

---

## Details of Each Module

1. **tool_converter.py**  
   - Responsible for converting Python functions into JSON schemas.  
   - The key method is `generate_schemas()`, which returns a dictionary containing schemas for multiple LLM providers.  

2. **llm_api/base_api.py**  
   - Abstract base class defining the uniform `generate(messages, tools)` method.  
   - All LLM API wrappers must subclass BaseLLMAPI.  

3. **llm_api/openai_api.py, anthropic_api.py, gemini_api.py, groq_api.py**  
   - Concrete wrappers implementing each provider’s unique request/response pattern.  

4. **llm_tools/message_handler.py**  
   - Normalizes messages into a standard format.  
   - Manages user text blocks, system prompts, tool calls, and image data.  

5. **llm_tools/llm_handler.py**  
   - The core orchestrator that calls the LLM, detects “tool_use” instructions, and executes the corresponding Python functions.  
   - Consolidates final text responses.  

6. **functions/math_tools.py**  
   - Sample set of math functions (tools) that demonstrate how to integrate your logic into the system.  

7. **main.py**  
   - A reference script showing how everything ties together.  
   - Instantiates the ToolConverter, creates schemas, picks an LLM, registers tools, sets the prompt, and interacts with the user.  

---

## Example Snippets

Here’s a snippet that shows how you might add a custom function “greet_user” to your main script:

```python
from tool_converter import ToolConverter
from llm_tools.llm_handler import LLMHandler
from llm_api.openai_api import OpenAIAPI

def calculate_dog_age(human_years: int) -> str:
    """Converts human years to approximate dog years using the common rule."""
    dog_years = human_years * 7
    return f"{human_years} human years is approximately {dog_years} dog years!"

if __name__ == "__main__":
    converter = ToolConverter()
    # Include your custom function
    functions = [calculate_dog_age]

    # Generate schemas
    schemas = converter.generate_schemas(functions)
    print("Schemas:", schemas["gemini"])  # Example: print the Gemini schema

    # Create LLM client
    gemini_client = GeminiAPI(model_name="gemini-2.0-flash-exp")

    # Use the handler
    llm_handler = LLMHandler(openai_client)
    llm_handler.register_functions(functions)
    llm_handler.set_tools(schemas["openai"])

    # Set system instructions (optional)
    llm_handler.set_system_prompt("You can convert human years to dog years with calculate_dog_age tool.")

    # Send user message
    response = llm_handler.send_user_message("I'm 25 years old, how old would I be as a dog?")
    print("LLM Response:", response)
```

---

## Contributing

We welcome issue reports, feature requests, and pull requests. Please open a GitHub Issue first to discuss significant changes or additions.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Enjoy building with this multi-LLM tool integration system!

