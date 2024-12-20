# tool_converter.py 
import inspect
import json
from typing import List, Callable, Dict
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

class ToolConverter:
    """
    A utility class designed to convert Python functions into JSON schemas that can be used
    with various LLMs (OpenAI, Anthropic, Gemini, Groq). It:
    - Extracts Python function source code and docstrings.
    - Uses an OpenAI model to generate a JSON schema describing the function's parameters and return values.
    - Transforms the resulting OpenAI schema into formats for Anthropic, Gemini, and Groq platforms.
    """

    def __init__(self, indent_size: int = 4, client: OpenAI = None):
        """
        Initialize the ToolConverter with an optional custom indentation and OpenAI client.

        Args:
            indent_size (int): Number of spaces for JSON indentation, default is 4.
            client (OpenAI, optional): An OpenAI client instance. If not provided, a new one will be created.

        Example:
            converter = ToolConverter(indent_size=2)
        """
        self.indent_size = indent_size
        self.client = client if client else OpenAI()

    def _get_function_source(self, func: Callable) -> str:
        """
        Retrieve the full source code of a given Python function, including its docstring,
        and normalize indentation.

        Args:
            func (Callable): The Python function to process.

        Returns:
            str: The source code of the function with normalized indentation.
        """
        source = inspect.getsource(func)
        lines = source.split('\n')
        if lines:
            # Deduce indentation from the first line and remove it from all lines
            first_line_indent = len(lines[0]) - len(lines[0].lstrip())
            lines = [line[first_line_indent:] if line.startswith(' ' * first_line_indent) else line 
                     for line in lines]
        return '\n'.join(lines)

    def convert_functions_to_string(self, functions: List[Callable]) -> List[str]:
        """
        Convert a list of Python functions into a list of their source code strings.

        Args:
            functions (List[Callable]): Functions to convert.

        Returns:
            List[str]: Each element is the source code of a corresponding function.
        """
        function_strings = []
        for func in functions:
            function_strings.append(self._get_function_source(func))
        return function_strings
    
    def create_function_schema(self, function_string: str) -> Dict:
        """
        Generate a JSON schema for a function by sending its source code to the OpenAI model.

        The model receives a system and user message instructing it to produce a JSON schema
        that includes a 'type': 'function' at the root, a 'function' block with 'name',
        'description', 'strict': false, and 'parameters' detailing each parameter.

        Args:
            function_string (str): The source code of a single function.

        Returns:
            Dict: The JSON schema for the given function.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "(\"\"\"### JSON Schema Generator\n"
                               "    Your primary role is to convert provided function details into JSON schemas. The schemas should be clear, structured, and follow a specific format.\n\n"
                               "    ### Schema Structure:\n"
                               "    Each schema must start with a `\"type\": \"function\"` key. The function details should be nested under a `\"function\"` key.\n\n"
                               "    ### Schema Format:\n"
                               "    - **name**: The function's name.\n"
                               "    - **description**: A brief description of what the function does.\n"
                               "    - **strict**: A required key set to `false`.\n"
                               "    - **parameters**: An object detailing the parameters the function accepts.\n"
                               "      - **type**: Always `\"object\"`.\n"
                               "      - **properties**: An object where each key is a parameter name and its value is an object with `\"type\"` and `\"description\"`.\n"
                               "      - **required**: An array of parameter names that are required.\n"
                               "      - **additionalProperties**: Must be set to `false`.\n\n"
                               "    ### Examples:\n"
                               "    Example 1:\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"bing_search\",\n"
                               "        \"description\": \"Searches Bing with a provided query and returns relevant web search results.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"query\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"The search query for Bing Search.\"\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"query\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    Example 2:\n"
                               "    ```json\n"
                               "        {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"manage_notes\",\n"
                               "        \"description\": \"Manage notes in a text file for later use.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"action\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"The action to perform on the notes file.\",\n"
                               "              \"enum\": [\"create\", \"update\", \"retrieve\", \"clear\"]\n"
                               "            },\n"
                               "            \"content\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"The content for 'create' and 'update' actions.\"\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"action\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    ### Template:\n"
                               "    ```json\n"
                               "        {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"new_tool\",\n"
                               "        \"description\": \"This is a template that you can start from to build your tool\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"array_property_name\": {\n"
                               "              \"description\": \"A property that returns an array of items (can be any type mentioned below, including an object)\",\n"
                               "              \"items\": {\n"
                               "                \"type\": \"string\"\n"
                               "              },\n"
                               "              \"type\": \"array\"\n"
                               "            },\n"
                               "            \"boolean_property_name\": {\n"
                               "              \"description\": \"A property that returns a boolean\",\n"
                               "              \"type\": \"boolean\"\n"
                               "            },\n"
                               "            \"enum_property_name\": {\n"
                               "              \"description\": \"A property that returns a value from a list of enums (can be any type)\",\n"
                               "              \"enum\": [\n"
                               "                \"option 1\",\n"
                               "                \"option 2\",\n"
                               "                \"option 3\"\n"
                               "              ],\n"
                               "              \"type\": \"string\"\n"
                               "            },\n"
                               "            \"number_property_name\": {\n"
                               "              \"description\": \"A property that returns a number\",\n"
                               "              \"type\": \"number\"\n"
                               "            },\n"
                               "            \"object_property_name\": {\n"
                               "              \"description\": \"A property that returns an object\",\n"
                               "              \"properties\": {\n"
                               "                \"foo\": {\n"
                               "                  \"description\": \"A property on the object called 'foo' that returns a string\",\n"
                               "                  \"type\": \"string\"\n"
                               "                },\n"
                               "                \"bar\": {\n"
                               "                  \"description\": \"A property on the object called 'bar' that returns a number\",\n"
                               "                  \"type\": \"number\"\n"
                               "                }\n"
                               "              },\n"
                               "              \"additionalProperties\": false\n"
                               "            },\n"
                               "            \"string_property_name\": {\n"
                               "              \"description\": \"A property that returns a string\",\n"
                               "              \"type\": \"string\"\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\n"
                               "            \"array_property_name\",\n"
                               "            \"number_property_name\"\n"
                               "          ],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    ### Additional Complex Examples:\n"
                               "    Example 3 (Nested Objects):\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"create_user_profile\",\n"
                               "        \"description\": \"Creates a user profile with nested address information.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"username\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"The desired username.\"\n"
                               "            },\n"
                               "            \"age\": {\n"
                               "              \"type\": \"number\",\n"
                               "              \"description\": \"The user's age in years.\"\n"
                               "            },\n"
                               "            \"address\": {\n"
                               "              \"type\": \"object\",\n"
                               "              \"properties\": {\n"
                               "                \"street\": {\n"
                               "                  \"type\": \"string\",\n"
                               "                  \"description\": \"Street name of the user's address.\"\n"
                               "                },\n"
                               "                \"city\": {\n"
                               "                  \"type\": \"string\",\n"
                               "                  \"description\": \"City name where the user resides.\"\n"
                               "                },\n"
                               "                \"zipcode\": {\n"
                               "                  \"type\": \"string\",\n"
                               "                  \"description\": \"Postal code of the address.\"\n"
                               "                }\n"
                               "              },\n"
                               "              \"required\": [\"street\", \"city\"],\n"
                               "              \"additionalProperties\": false\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"username\", \"address\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    Example 4 (Arrays of Objects):\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"batch_process_items\",\n"
                               "        \"description\": \"Processes a batch of items, each with its own attributes.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"items\": {\n"
                               "              \"type\": \"array\",\n"
                               "              \"description\": \"A list of items to process.\",\n"
                               "              \"items\": {\n"
                               "                \"type\": \"object\",\n"
                               "                \"properties\": {\n"
                               "                  \"id\": {\n"
                               "                    \"type\": \"number\",\n"
                               "                    \"description\": \"Unique identifier for the item.\"\n"
                               "                  },\n"
                               "                  \"value\": {\n"
                               "                    \"type\": \"string\",\n"
                               "                    \"description\": \"Value associated with the item.\"\n"
                               "                  }\n"
                               "                },\n"
                               "                \"required\": [\"id\", \"value\"],\n"
                               "                \"additionalProperties\": false\n"
                               "              }\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"items\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    Example 5 (Enum Types and Arrays):\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"filter_records\",\n"
                               "        \"description\": \"Filters records based on a set of criteria.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"status\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"Status to filter by.\",\n"
                               "              \"enum\": [\"active\", \"inactive\", \"pending\"]\n"
                               "            },\n"
                               "            \"tags\": {\n"
                               "              \"type\": \"array\",\n"
                               "              \"description\": \"List of tags to match.\",\n"
                               "              \"items\": {\n"
                               "                \"type\": \"string\"\n"
                               "              }\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"status\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    Example 6 (Complex Nested Structures):\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"analyze_data\",\n"
                               "        \"description\": \"Analyzes complex data with nested structures and multiple enum fields.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"metadata\": {\n"
                               "              \"type\": \"object\",\n"
                               "              \"properties\": {\n"
                               "                \"source\": {\n"
                               "                  \"type\": \"string\",\n"
                               "                  \"description\": \"The data source identifier.\"\n"
                               "                },\n"
                               "                \"timestamp\": {\n"
                               "                  \"type\": \"string\",\n"
                               "                  \"description\": \"ISO 8601 timestamp of when the data was collected.\"\n"
                               "                }\n"
                               "              },\n"
                               "              \"required\": [\"source\"],\n"
                               "              \"additionalProperties\": false\n"
                               "            },\n"
                               "            \"data_points\": {\n"
                               "              \"type\": \"array\",\n"
                               "              \"description\": \"An array of data points to be analyzed.\",\n"
                               "              \"items\": {\n"
                               "                \"type\": \"object\",\n"
                               "                \"properties\": {\n"
                               "                  \"value\": {\n"
                               "                    \"type\": \"number\",\n"
                               "                    \"description\": \"Numeric value of the data point.\"\n"
                               "                  },\n"
                               "                  \"type\": {\n"
                               "                    \"type\": \"string\",\n"
                               "                    \"description\": \"Type/category of the data point.\",\n"
                               "                    \"enum\": [\"metric\", \"dimension\", \"event\"]\n"
                               "                  },\n"
                               "                  \"attributes\": {\n"
                               "                    \"type\": \"object\",\n"
                               "                    \"properties\": {\n"
                               "                      \"quality\": {\n"
                               "                        \"type\": \"string\",\n"
                               "                        \"enum\": [\"high\", \"medium\", \"low\"],\n"
                               "                        \"description\": \"Quality level of the data point.\"\n"
                               "                      },\n"
                               "                      \"annotations\": {\n"
                               "                        \"type\": \"array\",\n"
                               "                        \"description\": \"List of annotations associated with the data point.\",\n"
                               "                        \"items\": {\n"
                               "                          \"type\": \"string\"\n"
                               "                        }\n"
                               "                      }\n"
                               "                    },\n"
                               "                    \"additionalProperties\": false\n"
                               "                  }\n"
                               "                },\n"
                               "                \"required\": [\"value\", \"type\"],\n"
                               "                \"additionalProperties\": false\n"
                               "              }\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"metadata\", \"data_points\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    Example 7 (Multiple Required Enums and Nested Arrays):\n"
                               "    ```json\n"
                               "    {\n"
                               "      \"type\": \"function\",\n"
                               "      \"function\": {\n"
                               "        \"name\": \"configure_system\",\n"
                               "        \"description\": \"Configures a system with a set of parameters and nested operations.\",\n"
                               "        \"strict\": false,\n"
                               "        \"parameters\": {\n"
                               "          \"type\": \"object\",\n"
                               "          \"properties\": {\n"
                               "            \"operation_mode\": {\n"
                               "              \"type\": \"string\",\n"
                               "              \"description\": \"The mode in which the system should operate.\",\n"
                               "              \"enum\": [\"automatic\", \"manual\"]\n"
                               "            },\n"
                               "            \"tasks\": {\n"
                               "              \"type\": \"array\",\n"
                               "              \"description\": \"A list of tasks to be scheduled.\",\n"
                               "              \"items\": {\n"
                               "                \"type\": \"object\",\n"
                               "                \"properties\": {\n"
                               "                  \"task_name\": {\n"
                               "                    \"type\": \"string\",\n"
                               "                    \"description\": \"The name of the task.\"\n"
                               "                  },\n"
                               "                  \"frequency\": {\n"
                               "                    \"type\": \"string\",\n"
                               "                    \"description\": \"How often the task should run.\",\n"
                               "                    \"enum\": [\"daily\", \"weekly\", \"monthly\"]\n"
                               "                  },\n"
                               "                  \"parameters\": {\n"
                               "                    \"type\": \"object\",\n"
                               "                    \"properties\": {\n"
                               "                      \"threshold\": {\n"
                               "                        \"type\": \"number\",\n"
                               "                        \"description\": \"A numerical threshold for the task.\"\n"
                               "                      },\n"
                               "                      \"flags\": {\n"
                               "                        \"type\": \"array\",\n"
                               "                        \"description\": \"List of optional flags.\",\n"
                               "                        \"items\": {\n"
                               "                          \"type\": \"string\"\n"
                               "                        }\n"
                               "                      }\n"
                               "                    },\n"
                               "                    \"additionalProperties\": false\n"
                               "                  }\n"
                               "                },\n"
                               "                \"required\": [\"task_name\", \"frequency\"],\n"
                               "                \"additionalProperties\": false\n"
                               "              }\n"
                               "            }\n"
                               "          },\n"
                               "          \"required\": [\"operation_mode\", \"tasks\"],\n"
                               "          \"additionalProperties\": false\n"
                               "        }\n"
                               "      }\n"
                               "    }\n"
                               "    ```\n\n"
                               "    ### Requirements:\n\n"
                               "    1.\tUse exact naming conventions and parameter names from the provided function.\n"
                               "    2.\tEnsure the schema is a valid JSON object.\n"
                               "    3.\tMaintain the specified format and structure in your response.\n\n"
                               "    The aim is to provide users with a JSON schema that precisely matches the functionality of the given function, aiding in their software development projects.\n\n"
                               "    You should concentrate on defining each function’s name, description, parameters, and required fields in a JSON format, adhering to the structure shown in these examples. The aim is to provide users with a JSON schema that precisely matches the functionality of the given function. You’re not tasked with creating Python schemas but rather converting the function details into the correct JSON schema format.\n"
                               "    Your primary role is to convert provided function details into JSON schemas. The schemas should be clear, structured, and follow a specific format.\n\"\"\")"
                },
                {
                    "role": "user",
                    "content": f"Generate a valid schema for the following: {function_string}"
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.5,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content
    
    
    def create_function_schemas(self, function_strings: List[str], max_workers: int = None) -> str:
        """
        Creates JSON schemas for multiple functions in parallel, then merges them into a single JSON string.

        Args:
            function_strings (List[str]): Source code strings for the functions.
            max_workers (int, optional): Number of threads for parallel execution. Defaults to 10.

        Returns:
            str: A JSON-formatted string containing a list of all generated schemas.
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            schema_futures = executor.map(self.create_function_schema, function_strings)
            
            schemas = []
            for schema in schema_futures:
                schema_dict = json.loads(schema)
                schemas.append(schema_dict)
            
            combined_schema = json.dumps(schemas, indent=2)
            return combined_schema

    def convert_openai_to_anthropic(self, openai_schema):
        """
        Convert the OpenAI schema format into Anthropic format.

        Anthropic format requires a 'name', 'description', and 'input_schema' key, where 'input_schema'
        details parameters similarly to OpenAI but without the 'type': 'function' wrapper.

        Args:
            openai_schema (list): List of tool definitions in OpenAI format.

        Returns:
            list: Tool definitions reformatted for Anthropic.
        """
        anthropic_schema = []
        for tool in openai_schema:
            function_details = tool.get("function", tool)
            
            anthropic_tool = {
                "name": function_details["name"],
                "description": function_details["description"],
                "input_schema": {
                    "type": "object",
                    "properties": function_details["parameters"]["properties"],
                    "required": function_details["parameters"].get("required", [])
                }
            }
            anthropic_schema.append(anthropic_tool)
        
        return anthropic_schema
    
    def convert_openai_to_gemini(self, openai_schema):
        """
        Convert the OpenAI schema format into Gemini format.

        Gemini format is similar to OpenAI's but does not include 'strict' or 'additionalProperties'.
        It retains 'name', 'description', and a 'parameters' object structured as an object with
        'properties' and 'required'.

        Args:
            openai_schema (list): List of tool definitions in OpenAI format.

        Returns:
            list: Tool definitions suitable for Gemini.
        """
        gemini_schema = []
        
        for tool in openai_schema:
            function_details = tool.get("function", tool)
            
            parameters = {
                "type": "object",
                "properties": function_details["parameters"]["properties"],
                "required": function_details["parameters"].get("required", [])
            }
            
            gemini_tool = {
                "type": "function",
                "function": {
                    "name": function_details["name"],
                    "description": function_details["description"],
                    "parameters": parameters
                }
            }
            gemini_schema.append(gemini_tool)
        
        return gemini_schema
    

    def generate_schemas(self, functions: List[Callable]) -> dict:
        """
        Generate schemas for OpenAI, Anthropic, Gemini, and Groq by:
        1. Converting functions to source strings.
        2. Generating an OpenAI-style schema.
        3. Converting that schema into Anthropic, Gemini, and Groq formats.

        Args:
            functions (List[Callable]): The Python functions to convert.

        Returns:
            dict: A dictionary with 'openai', 'anthropic', 'gemini', and 'groq' keys, each containing their respective schemas.
        """
        function_strings = self.convert_functions_to_string(functions)
        
        openai_schema = self.create_function_schemas(function_strings)
        openai_parsed = json.loads(openai_schema)
        
        anthropic_schema = self.convert_openai_to_anthropic(openai_parsed)
        gemini_schema = self.convert_openai_to_gemini(openai_parsed)
        groq_schema = openai_parsed

        return {
            "openai": openai_parsed,
            "anthropic": anthropic_schema,
            "gemini": gemini_schema,
            "groq": groq_schema
        }

# Example usage
def print_text(text):
    """prints any text sent to the function and returns confirmation"""
    print(text)
    return "Text is printed"

def add_numbers(a, b):
    """adds two numbers together"""
    return a + b

if __name__ == "__main__":
    # Create converter and generate all schemas
    converter = ToolConverter()
    functions = [print_text, add_numbers]
    schemas = converter.generate_schemas(functions)

    # Print all schemas
    print("OpenAI")
    print(schemas["openai"])
    print("Groq")
    print(schemas["groq"])
    print("Anthropic")
    print(schemas["anthropic"])
    print("Gemini")
    print(schemas["gemini"])