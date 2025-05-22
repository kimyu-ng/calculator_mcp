import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    SseServerParams,
)

load_dotenv()

print(os.getenv("MY_OPENAI_API_KEY"))

root_agent = LlmAgent(
    model=LiteLlm(
        model="openai/gpt-4.1-nano",
        api_key=os.getenv("MY_OPENAI_API_KEY"),
    ),
    name="CalculatorAgent",
    instruction="""Help user to perform calculations using the calculator tools.
    Once you compute the result, always show step by step calculation.
    """,
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url="http://localhost:8001/sse",
            )
        )
    ],
)
