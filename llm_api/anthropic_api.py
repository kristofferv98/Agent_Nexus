# llm_api/anthropic_api.py
import os
from typing import List, Dict
from anthropic import Anthropic
from llm_api.base_api import BaseLLMAPI

class AnthropicAPI(BaseLLMAPI):
    """
    Anthropic LLM API integration.
    """
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620", VERBOSE=False, CONFIRMATION_PRINT=False):
        self.model_name = model_name
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("No ANTHROPIC_API_KEY found.")
        self.client = Anthropic(api_key=api_key)
        self.VERBOSE = VERBOSE
        self.CONFIRMATION_PRINT = CONFIRMATION_PRINT

    def _convert_messages(self, messages: List[Dict]):
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
                # Treat tool messages as user messages containing the tool result
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
        system_prompt, anthropic_messages = self._convert_messages(messages)
        params = {
            "model": self.model_name,
            "messages": anthropic_messages,
            "max_tokens": 4096,
            "temperature": 0,
            "system": system_prompt
        }

        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)
        if self.VERBOSE:
            print("Anthropic raw api response:", response)
        if self.CONFIRMATION_PRINT:
            print("ANTHROPIC RESPONSE RECEIVED")

        content_blocks = []
        has_tool_calls = False

        for block in response.content:
            if block.type == "text" and block.text.strip():
                content_blocks.append({"type":"text","text":block.text.strip()})
            elif block.type == "tool_use":
                has_tool_calls = True
                content_blocks.append({
                    "type":"tool_use",
                    "id":block.id,
                    "name":block.name,
                    "input":block.input
                })

        return {
            "content": content_blocks,
            "stop_reason": "tool_use" if has_tool_calls else "stop_sequence"
        }   