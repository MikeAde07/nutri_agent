# Nutritional AI Agent 
- ## Enter your personal info such as age, weight, height, goals (muscle loss, fat loss, Stay Active) and notes/dietary preferences in order to recieve nutritional/dietary info to acheive goals.

## 🪀Features
- Streamlit front-end
- Langchain framework used to build AI Agent
- connected to OpenAI LLM
- Astra DB vector database for data storage/persistence
- Meal plans/Recipes provided based off User's profile info via Spoonacular API
- Caloric calculation
- Food Image Classifier/Recognition model via Replicate

## 👨🏾‍💻Tech Stack
- **Frontend**: Streamlit
- **Backend**: Langchain, OpenAI (GPT)
- **RAG**: Astra DB
- **Environment**: Python 3.12
- **Tools**: Meal Plan/Recipes, Calorie calculations, Vector Search, OpenAI API, Food Image classification

## Getting Started
1. Clone the Repository:
   git clone https://github.com/MikeAde07/nutri_agent.git
2. Set up environment:
   Create a .env file in the root directory and add your OpenAI API key:
   OPENAI_API_KEY=your_openai_key
   SPOONACULAR_API_KEY=your_spoonacular_key
   ASTRA_DB_APPLICATION_TOKEN=your_astra_db_key
   ASTRA_ENDPOINT=your_astra_endpoint_key
   REPLICATE_API_TOKEN=your_replicate_key
3. Build and Run with Docker:
   (To be continued/In-Progress)

## 📂Folder Structure
- stream.py (Streamlit app logic)
- agent_utils.py (AI Agent logic)
- tools_utils.py (utility tools used by Agent)
- db.py (database collection creation logic)
- profiles.py (User profile)
- form_submit.py (update user personal info)
- requirements.txt
- .env
- README.md


## 🔨 Agent Tools Used
| Tool | Description |
|------|-------------|
|  get_meal_plan   | Retrieves Meal Plan based on users calculated caloric needs via Spoonacular API            |
| calorie_calculator_tool      |    Calculates users caloric intake/needs based on goals (muscle gain,  Fat Loss, Stay Active) |
|identify_food_image| Food identification based off of images uploaded by users|
|nutrition_from_food| provides nutritional information from food classification of image provided by user|
