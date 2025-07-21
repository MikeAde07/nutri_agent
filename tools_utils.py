import os
import requests
from langchain.agents import Tool
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv

class ProfileInput(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    gender: Literal["Male", "Female", "Other"]
    activity_level: str
    goals: list[str]


load_dotenv()



def calculate_calories(profile: ProfileInput) -> dict:
    weight_kg = profile.weight_kg 
    height_cm = profile.height_cm 
    age = profile.age 
    gender = profile.gender 
    activity_level = profile.activity_level
    # Assume the first goal is the primary one
    goal = profile.goals[0] if profile.goals else "Stay Active"

    #Normalize goal to lowercase once
    goal = goal.lower()

    #Activity mulitplier; accepted standard in the across fitness and medical communities
    activity_multipliers =  {
        "Sedentary": 1.2, 
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Super Active": 1.9,
    }

    #Basic Metabloic Rate (Mifflin-St Jeor Equation)
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    bmr += 5 if gender == "Male" else -161
    
    # Total Daily Enery Expenditure
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)

    # Adjust calories by goal
    if goal == "fat loss":
        calorie_target = tdee - 500
    elif goal == "muscle gain":
        calorie_target = tdee + 300
    #Stay Active/Maintenance
    else: 
        calorie_target = tdee

    #Macro split
    if goal == "fat loss":
        protein_pct = 0.4
        fat_pct = 0.3
        carb_pct = 0.3
    elif goal == "muscle gain":
        protein_pct = 0.3
        fat_pct = 0.25
        carb_pct = 0.45
    else:
        protein_pct = 0.3
        fat_pct = 0.3
        carb_pct = 0.4

    #Macro breakdown/convert to grams
    protein_grams = round((calorie_target * protein_pct)/4)
    fat_grams = round((calorie_target * fat_pct)/9)
    carb_grams = round((calorie_target * carb_pct)/4)


    return {
        "goal": goal.title(),
        "calories": round(calorie_target),
        "protein": protein_grams,
        "fat": fat_grams,
        "carbs": carb_grams,
    }



@tool
def calorie_calculator_tool(profile: ProfileInput) -> dict:
    """Estimate daily calories and macro targets based on user stats and fitness goals"""
    return calculate_calories(profile)

@tool
def get_meal_plan(profile: ProfileInput):
    """Uses spoonacular api functionality to provide meal plans due to users needs and dietary preferences and nutritonal breakdowns"""
   
    calorie_data = calculate_calories(profile)
    estimated_calories = calorie_data["calories"]

    api_key = os.getenv("SPOONACULAR_API_KEY")

    url="https://api.spoonacular.com/mealplanner/generate"

    params={
        "timeFrame": "day",
        "targetCalories": estimated_calories,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)

    data = response.json()

    return {
        "estimated_calories": estimated_calories,
        "meal_plan": data.get("meals",[]),
        "nutrients": data.get("nutrients", {})}




