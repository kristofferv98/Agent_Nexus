# llm_api/groq_api.py
import os
import json
from typing import List, Dict
from llm_api.base_api import BaseLLMAPI
from openai import OpenAI

url = "https://api.groq.com/openai/v1"

class GroqAPI(BaseLLMAPI):
    """
    GROQ LLM API integration.
    Uses OpenAI-compatible API endpoint at Groq.
    """
    def __init__(self, model_name: str = "llama-3.3-70b-specdec", VERBOSE=False, CONFIRMATION_PRINT=False):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("No GROQ_API_KEY found.")
        
        self.client = OpenAI(api_key=api_key, base_url=url)
        self.model = model_name
        self.VERBOSE = VERBOSE
        self.CONFIRMATION_PRINT = CONFIRMATION_PRINT

    def _to_groq_messages(self, messages: List[Dict]) -> List[Dict]:
        groq_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "tool":
                tool_call_id = msg.get("tool_call_id")
                if not tool_call_id:
                    raise ValueError("Missing tool_call_id in tool message.")
                text_content = " ".join(b.get("text","") for b in msg["content"] if b["type"]=="text")
                groq_messages.append({
                    "role":"tool",
                    "tool_call_id":tool_call_id,
                    "content": text_content if text_content else ""
                })
                continue

            content_blocks = msg["content"]
            text_parts = []
            tool_calls = []
            for block in content_blocks:
                if not isinstance(block, dict):
                    block = {"type":"text","text":str(block)}
                btype = block.get("type","text")
                if btype == "text":
                    text_parts.append(block.get("text",""))
                elif btype == "tool_use":
                    tool_calls.append({
                        "id": block["id"],
                        "type": "function",
                        "function": {
                            "name": block["name"],
                            "arguments": json.dumps(block["input"])
                        }
                    })
                elif btype == "image":
                    text_parts.append("[Image data omitted]")

            text_content = " ".join(text_parts).strip()

            if role == "assistant" and tool_calls:
                m = {"role": "assistant"}
                if text_content:
                    m["content"] = text_content
                m["tool_calls"] = tool_calls
                groq_messages.append(m)
            else:
                groq_messages.append({
                    "role": role,
                    "content": text_content if text_content else ""
                })

        return groq_messages

    def generate(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        groq_messages = self._to_groq_messages(messages)
        params = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": 0
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        if self.VERBOSE:
            print("Groq raw api response:", response)
        if self.CONFIRMATION_PRINT:
            print("GROQ RESPONSE RECEIVED")

        message = response.choices[0].message
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append({
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": json.loads(tc.function.arguments)
                })
            return {"content": tool_calls, "stop_reason": "tool_use"}

        return {
            "content": [{"type":"text","text":message.content}],
            "stop_reason":"stop_sequence"
        }