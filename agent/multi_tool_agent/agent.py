"""
agent.py
--------
This module configures and instantiates the root LLM agent for the Agentic Garak system. It sets up the language model, system prompt, and integrates the Garak vulnerability scanning tools.
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .GarakWrapper import run_scan , list_probes
from google.genai import types





# Configure the LLM model (Ollama mistral in this case)
model = LiteLlm(
    model="ollama_chat/magistral:24b-small-2506-q8_0",
    # api_base is a local API URL for internal service communication, not a secret or credential
    api_base="http://host.docker.internal:11434",
)

# System prompt: instructs the LLM on how to behave, what to say, and what to avoid
system_prompt = """

# Agentic Garak System Prompt



You are an assistant specialized in performing Garak LLM vulnerability scans.
When the user asks you to run an scan, collect exactly these two parameters:
  • model_name  
  • probes  
   
If any are missing, ask only for the missing ones (e.g. “Please provide the missing parameter(s): probes.”).  
When the user explicitly requests available probes or probe (or omits list probes), invoke the list_probes tool.  
When all parameters are present, invoke the run_scan tool.  
For any other questions, reply normally and conversationally.
"""

# Create the root agent with the model, tools, and instructions
root_agent = LlmAgent(
    name="agent",
    model=model,
    tools=[run_scan, list_probes],
    instruction=system_prompt,
    
)

