# llm_api/gemini_api.py

import os
from typing import List, Dict
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from llm_api.base_api import BaseLLMAPI

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Map JSON schema types to Gemini content.Type
def map_json_type_to_content_type(json_type: str) -> content.Type:
    json_type = json_type.lower()
    if json_type == "string":
        return content.Type.STRING
    elif json_type == "number":
        return content.Type.NUMBER
    elif json_type == "boolean":
        return content.Type.BOOL
    elif json_type == "array":
        return content.Type.ARRAY
    elif json_type == "object":
        return content.Type.OBJECT
    else:
        return content.Type.OBJECT

def convert_schema_to_gemini(parameters: dict) -> content.Schema:
    """
    Recursively convert the JSON schema to Gemini schema.
    """
    schema_type = parameters.get("type", parameters.get("type_", "object"))
    ctype = map_json_type_to_content_type(schema_type)
    schema_builder = content.Schema(type=ctype)

    # Required fields
    required_fields = parameters.get("required", [])
    if required_fields:
        schema_builder.required.extend(required_fields)

    # Enum
    if "enum" in parameters:
        schema_builder.enum[:] = parameters["enum"]

    # Properties if object
    props = parameters.get("properties", {})
    for prop_name, prop_schema in props.items():
        child_schema = convert_schema_to_gemini(prop_schema)
        schema_builder.properties[prop_name] = child_schema

    # Items if array
    if ctype == content.Type.ARRAY:
        items = parameters.get("items", {})
        if items:
            item_schema = convert_schema_to_gemini(items)
            schema_builder.items.CopyFrom(item_schema)

    # Description
    description = parameters.get("description")
    if description:
        schema_builder.description = description

    return schema_builder

def convert_tool_schema_to_gemini(tools_schema: list[dict]) -> List[genai.protos.Tool]:
    """
    Converts a list of tool definitions (OpenAI-like schema) to Gemini tools.
    """
    declarations = []
    for tool in tools_schema:
        function_details = tool["function"]
        name = function_details["name"]
        description = function_details.get("description", "")
        params = function_details.get("parameters", {})
        gemini_schema = convert_schema_to_gemini(params)

        fd = genai.protos.FunctionDeclaration(
            name=name,
            description=description,
            parameters=gemini_schema
        )
        declarations.append(fd)

    return [genai.protos.Tool(function_declarations=declarations)]

class GeminiAPI(BaseLLMAPI):
    """
    Gemini LLM integration.
    """
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", VERBOSE=False, CONFIRMATION_PRINT=False, tools_schema=None):
        self.model_name = model_name
        self.VERBOSE = VERBOSE
        self.CONFIRMATION_PRINT = CONFIRMATION_PRINT

        # Convert provided schema to Gemini format if given
        gemini_tools = []
        if tools_schema:
            gemini_tools = convert_tool_schema_to_gemini(tools_schema)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            tools=gemini_tools,
        )

    def _convert_messages(self, messages: List[Dict]):
        """
        Convert internal message format into something suitable for the Gemini model.
        """
        system_prompt = ""
        normal_msgs = []
        for msg in messages:
            role = msg["role"]
            cblocks = msg["content"]

            if role == "system":
                stext = " ".join(b.get("text","") for b in cblocks if b["type"]=="text").strip()
                system_prompt = stext
                continue

            if role == "tool":
                # Treat tool messages as user messages containing tool result
                txt = " ".join(b.get("text","") for b in cblocks if b["type"]=="text").strip()
                tool_call_id = msg.get("tool_call_id")
                if tool_call_id:
                    text_content = f"Tool result for {tool_call_id}: {txt}"
                else:
                    text_content = txt
                normal_msgs.append({"role":"user","content":text_content})
                continue

            # For user/assistant normal messages
            msg_text = " ".join(b.get("text","") for b in cblocks if b["type"]=="text").strip()
            if msg_text:
                normal_msgs.append({"role":role,"content":msg_text})

        return system_prompt, normal_msgs

    def generate(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        system_prompt, gen_messages = self._convert_messages(messages)

        params = {
            "model": self.model_name,
            "messages": gen_messages,
            "max_tokens": 4096,
            "temperature": 0,
            "system": system_prompt
        }

        # Gemini python client does not have a direct 'tools' param here,
        # since we provided them at model creation time.

        response = self.model.start_chat(enable_automatic_function_calling=False, history=[]).send_message(gen_messages[-1]["content"])
        if self.VERBOSE:
            print("Gemini raw api response:", response)
        if self.CONFIRMATION_PRINT:
            print("GEMINI RESPONSE RECEIVED")

        # The response is a google.generativeai result. Extract content blocks.
        content_blocks = []
        has_tool_calls = False

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    content_blocks.append({"type":"text","text":part.text.strip()})
                elif part.function_call:
                    has_tool_calls = True
                    content_blocks.append({
                        "type":"tool_use",
                        "id": part.function_call.name, # Gemini does not provide an id, we could generate one
                        "name": part.function_call.name,
                        "input": part.function_call.args
                    })

        return {
            "content": content_blocks,
            "stop_reason": "tool_use" if has_tool_calls else "stop_sequence"
        }