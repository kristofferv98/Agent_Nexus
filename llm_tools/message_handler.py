# llm_tools/message_handler.py
import base64
import mimetypes
from typing import List, Dict, Union

class MessageHandler:
    """
    Handles formatting and storage of messages in a standardized format.
    """
    def __init__(self):
        self.messages = []

    def set_system_prompt(self, system_prompt: str):
        # Insert or update system message
        for msg in self.messages:
            if msg.get("role") == "system":
                msg["content"] = [{"type":"text","text":system_prompt}]
                return
        self.messages.insert(0, {"role":"system","content":[{"type":"text","text":system_prompt}]})

    def append_message(self, role: str, content_blocks: Union[str, Dict, List[Dict]]):
        if role == "tool":
            if isinstance(content_blocks, dict) and "tool_call_id" in content_blocks and "content" in content_blocks:
                tool_call_id = content_blocks["tool_call_id"]
                tool_content_str = content_blocks["content"]
                self.messages.append({
                    "role":"tool",
                    "tool_call_id": tool_call_id,
                    "content":[{"type":"text","text":tool_content_str}]
                })
                return
            else:
                raise ValueError("Tool messages must be dict with 'tool_call_id' and 'content' keys.")
        
        if isinstance(content_blocks, str):
            content_blocks = [{"type":"text","text":content_blocks}]
        elif isinstance(content_blocks, dict):
            if "type" not in content_blocks:
                content_blocks = [{"type":"text","text":str(content_blocks)}]
            else:
                content_blocks = [content_blocks]
        else:
            # It's a list
            normalized = []
            for block in content_blocks:
                if not isinstance(block, dict):
                    normalized.append({"type":"text","text":str(block)})
                else:
                    if "type" not in block:
                        block["type"] = "text"
                    normalized.append(block)
            content_blocks = normalized

        self.messages.append({"role": role, "content": content_blocks})

    def append_user_text(self, text: str):
        self.append_message("user", text)

    def append_image(self, role: str, image_path: str, text_comment: str = None):
        image_data = self.encode_image_to_base64(image_path)
        image_block = {"type":"image","source":{"type":"base64","media_type":image_data["media_type"],"data":image_data["data"]}}
        blocks = [image_block]
        if text_comment:
            blocks.append({"type":"text","text":text_comment})
        self.append_message(role, blocks)

    def encode_image_to_base64(self, image_path: str):
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode("utf-8")
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
        return {"media_type": mime_type, "data": encoded}

    def get_messages(self) -> List[Dict]:
        return self.messages

    def reset(self):
        self.messages = []