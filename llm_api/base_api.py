# llm_api/base_api.py
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLMAPI(ABC):
    """
    Abstract base class for LLM APIs.
    Defines the interface that all LLM APIs must implement.
    """
    @abstractmethod
    def generate(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """
        Send the conversation and tool definitions to the LLM and get a response.
        
        :param messages: A list of messages in a standardized format.
        :param tools: A list of tools (functions) definitions that the LLM can call.
        :return: A dictionary containing the model's response.
        """
        pass