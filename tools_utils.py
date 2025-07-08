import os
import requests
from langchain.agents import Tool
from langchain.tools import Tool
#from tools.spoonacular_tool import get_meal_plan
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from dotenv import load_dotenv






load_dotenv()

#llm = OpenAI(temperature=0)

def get_meal_plan(input:str):
    #macros=input["macros"],
    #diet=input.get("diet",""),
    #exclude=input.get("exclude", ""),
    #api_key=input["api_key"]
    estimated_calories = 3000

    api_key = os.getenv("SPOONACULAR_API_KEY")

    url="https://api.spoonacular.com/mealplanner/generate"
    params={
        "timeFrame": "day",
        #"diet": diet,
        #"exclude": exclude,
        #"targetCalories": macros.get("calories", 2000),
        "targetCalories": estimated_calories,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    return response.json()

meal_planner_tool = Tool(
    name="Spoonacular",
    func=get_meal_plan,
    description="Generates a meal plan based on macros, weight, goal, and user preferences"
)

 




