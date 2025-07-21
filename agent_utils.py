from dotenv import load_dotenv
import requests
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools_utils import get_meal_plan, calorie_calculator_tool

# load environment variable file
load_dotenv()

class NurtiResponse(BaseModel):
    diet_plan: str
    summary: str
    meal_recommendations: str
    foods: list[str]
    tools_used: list[str]


parser = PydanticOutputParser(pydantic_object=NurtiResponse)

# instantiate llm model
llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an award winning exercise nutrionist that will offer expert nutritional advice to users based on their age, weight, activity levels, goals and dietary/cultural preferences. 
            Examples of advice would be but not limited too, meal plans, key nutrients, macros intake and levels, healthy snacks, eating habits/frequencies and how many times to eat during the day. 
            Answer the user query and use necessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions)

tools = [get_meal_plan, calorie_calculator_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# input from user
#query = input("Tell me about yourself")

# Run the agent
#raw_response = agent_executor.invoke({"query": query})
#print(raw_response)

def ask_ai(profile: dict, question: str):
    profile_string ="\n".join([f"{k}: {v}" for k,v in profile.items()])
    full_query = f"My profile:\n{profile_string}\n\nQuestion:\n{question}"

    raw_response = agent_executor.invoke({"query": full_query})

# Try parsing into structured response
    try:
        #structured_response = parser.parse(raw_response.get("output"))
        return parser.parse(raw_response.get("output"))
        #print(structured_response)
    except Exception as e: 
        return {"Error": str(e), "raw_output": raw_response.get("output")}
        #print("Error parsing response", e, "Raw Response - ", raw_response)


