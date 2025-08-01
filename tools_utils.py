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
from datetime import datetime
import replicate

class ProfileInput(BaseModel):
    id: int
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

@tool 
def identify_food_image(image_path: str) -> str:
    """Identifies food in an image using MiniGPT-4. Returns a description."""
    try:
        output = replicate.run(
            "daanelson/minigpt-4:e447a8583cffd86ce3b93f9c2cd24f2eae603d99ace6afa94b33a08e94a3cd06",
            input={"image": open(image_path, "rb"), 
                   "prompt":"What food is in this image?",
                   "top_p": 0.9,
                   "num_beams": 5,
                   "max_length": 4000,
                   "temperature": 1.32,
                   "max_new_tokens": 3000,
                   "repetition_penalty": 1
                   }
        )
        return output.strip()
    except Exception as e:
        return f"Error identifying food: {e}"
    

@tool
def nutrition_from_food(food_name: str) -> dict:
    """Takes a food name, searches spoonacular, and returns nutrition information."""
    try:
        api_key = os.getenv("SPOONACULAR_API_KEY")
        search_url = "https://api.spoonacular.com/recipes/complexSearch"
        search_params = {
            "query": food_name,
            "number": 1,
            "apiKey": api_key
        }
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()

        #Retry with lowercase if no results
        if not search_data.get("results"):
            search_params["query"] = food_name.lower()
            search_response = requests.get(search_url, params=search_params)
            search_data = search_response.json()

        if not search_data.get("results"):
            return {"error": f"No results found for '{food_name}'"}
        
        recipe_id = search_data["results"][0]["id"]
        nutrition_url = f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json"
        nutrition_params = {"apiKey": api_key}
        nutrition_response = requests.get(nutrition_url, params=nutrition_params)
        nutrition_data = nutrition_response.json()

        return {
            "food_name": food_name,
            "recipe_id": recipe_id,
            "nutrition": nutrition_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def extract_food_keyword(description: str) -> str:
    """Uses OpenAI to extract the main food keyword from a long image description."""
    try:
        llm = OpenAI(temperature=0.2)
        prompt = PromptTemplate(
            input_variables=["description"],
            template=(
                "Extract the most likely **search term** for a food from this sentence.\n"
                "Keep it simple: 1-3 words max.\n"
                "Avoid details like toppings or ingredients.\n"
                "Use lowercase only.\n\n"
                "Sentence: {description}\n"
                "Search Term:"
            )
            )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(description)
        #remove whitespaces and quotations
        return result.strip().strip('"').strip("'")
    except Exception as e:
        return f"Error extracting food keyword: {e}"
    
@tool
def get_meal_week(profile: ProfileInput):
    """Uses spoonacular api functionality to provide weekly meal plans due to users needs and dietary preferences and nutritonal breakdowns"""
    try:
        calorie_data = calculate_calories(profile)
        estimated_calories = calorie_data["calories"]
        profile_id = profile.id
        start_date = datetime.today().strftime('%Y-%m-%d')

        api_key = os.getenv("SPOONACULAR_API_KEY")
        if not api_key:
            return {"error": "Missing Spoonacular API key."}

        url=f"https://api.spoonacular.com/mealplanner/{profile}/week/{start_date}"

        params={
            #"username": profile_id,
            "targetCalories": estimated_calories,
            #"start-date": start_date,
            "apiKey": api_key
        }

        response = requests.get(url, params=params)

        # Check for bad HTTP status before calling .json()
        if response.status_code != 200:
            return{
                "error": f"API call failed with status code {response.status_code}",
                "text": response.text
            }

        try:
            data = response.json()
        except Exception as e:
            return {
                "error": f"JSON parsing failed: {e}",
                "raw__response": response.text
            }

        return {
            "estimated_calories": estimated_calories,
            "meal_plan": data.get("week",{}),
            #"nutrients": data.get("nutrients", {})
            #"week_plan": data
            }

    except Exception as e:
        return {"error": f"Exception in get_meal_week: {str(e)}"}


