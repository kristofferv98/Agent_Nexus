# llm_tools/llm_handler.py
from typing import Optional, Dict, Any, Callable, List
from llm_api.base_api import BaseLLMAPI
from llm_tools.message_handler import MessageHandler
from concurrent.futures import ThreadPoolExecutor
import json
import traceback

class LLMHandler:
    """
    High-level interface for interacting with the LLM API, handling messages and tools execution.
    """
    def __init__(self, api: BaseLLMAPI):
        self.api = api
        self.handler = MessageHandler()
        self.tools = None
        self.registered_functions: Dict[str, Callable] = {}
        self.processed_tool_ids = set()

    def set_tools(self, tools: List[Dict]):
        self.tools = tools

    def register_function(self, func: Callable):
        self.registered_functions[func.__name__] = func

    def register_functions(self, functions: List[Callable]):
        for func in functions:
            self.register_function(func)

    def set_model(self, api: BaseLLMAPI):
        self.api = api
        self.processed_tool_ids.clear()

    def set_system_prompt(self, system_prompt: str):
        self.handler.set_system_prompt(system_prompt)

    def send_user_message(self, user_text: str) -> str:
        self.handler.append_user_text(user_text)
        return self._process_interaction()

    def send_user_image_and_text(self, image_path: str, text_comment: Optional[str] = None) -> str:
        self.handler.append_image("user", image_path, text_comment)
        return self._process_interaction()

    def _process_interaction(self) -> str:
        while True:
            messages = self.handler.get_messages()
            try:
                response = self.api.generate(messages, self.tools)
            except Exception as e:
                print(f"Error during API call: {e}")
                print(traceback.format_exc())
                raise

            content = response.get("content", [])
            stop_reason = response.get("stop_reason", "stop_sequence")

            text_blocks = [c for c in content if c.get("type") == "text"]
            tool_uses = [c for c in content if c.get("type") == "tool_use"]

            if tool_uses:
                # Append assistant message containing tool_use
                self.handler.append_message("assistant", content)

                # Process tool calls
                tool_calls_to_process = [tc for tc in tool_uses if tc["id"] not in self.processed_tool_ids]

                with ThreadPoolExecutor() as executor:
                    futures = []
                    for tool_call in tool_calls_to_process:
                        tool_id = tool_call["id"]
                        tool_name = tool_call["name"]
                        tool_input = tool_call["input"]
                        futures.append((tool_id, executor.submit(self._execute_tool, tool_id, tool_name, tool_input)))

                    for tool_id, future in futures:
                        result_block = future.result()
                        self.processed_tool_ids.add(tool_id)
                        result_str = json.dumps(result_block["data"]) if isinstance(result_block["data"], dict) else str(result_block["data"])
                        self.handler.append_message("tool", {
                            "tool_call_id": tool_id,
                            "content": result_str
                        })

                continue  # After processing tools, re-generate

            if stop_reason != "tool_use":
                return " ".join(block.get("text","") for block in text_blocks if block.get("text"))

    def _execute_tool(self, tool_id: str, tool_name: str, tool_input: Dict[str, Any]) -> Dict:
        func = self.registered_functions.get(tool_name)
        if not func:
            return {"type":"tool_result","tool_use_id":tool_id,"data":{"error":f"Unknown tool '{tool_name}'"}}
        try:
            result = func(**tool_input)
            if not isinstance(result, dict):
                result = {"result": str(result)}
            return {"type":"tool_result","tool_use_id":tool_id,"data":result}
        except Exception as e:
            return {"type":"tool_result","tool_use_id":tool_id,"data":{"error":f"Error executing {tool_name}: {e}"}}