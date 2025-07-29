import streamlit as st
from profiles import create_profile, get_notes, get_profile 
from form_submit import update_personal_info, add_note, delete_note
from db import personal_data_collection
from agent_utils import ask_ai
from tools_utils import calorie_calculator_tool, identify_food_image, nutrition_from_food, extract_food_keyword

st.title("Personal Nutrition Tool")


@st.fragment()
def personal_data_form():
    with st.form("personal_data"):
        st.header("Personal Data")

        profile = st.session_state.profile

        name = st.text_input("Name", value=profile["general"]["name"])
        age = st.number_input("Age", min_value=1, max_value=120, step=1, value=profile["general"]["age"])
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, value=float(profile["general"]["weight"]))
        height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1, value=float(profile["general"]["height"]))
        genders = ["Male", "Female", "Other"]
        gender = st.radio('Gender', genders, genders.index(profile["general"].get("gender", "Male")))
        activities = (
            "Sedentary",
            "Lightly Active",
            "Moderately Active",
            "Very Active",
            "Super Active",
        )
        activity_level = st.selectbox("Activity Level", activities, index=activities.index(profile["general"].get("activity_level", "Sedentary")))

        personal_data_submit = st.form_submit_button("Save")
        if personal_data_submit:
            if all([name, age, weight, height, gender, activity_level]) :
                with st.spinner():
                    st.session_state.profile = update_personal_info(profile, "general", name=name, weight=weight, height=height, gender=gender, age=age, activity_level=activity_level)

                    #reload updated profile from DB
                    updated_profile = get_profile(st.session_state.profile_id)
                    st.session_state.profile = updated_profile

                    st.success('Information saved.')
                    #st.write("Updated profile from DB:", updated_profile)
            else:
                st.warning('Please fill in all of the data!')

@st.fragment()
def goals_form():
    profile = st.session_state.profile
    with st.form("goals_form"):
        st.header("Goals")
        goals = st.multiselect("Select your Goals", ["Muscle Gain", "Fat Loss", "Stay Active"],
                               default=profile.get("goals", ["Muscle Gain"]))
        
        goals_submit = st.form_submit_button('Save')
        if goals_submit:
            if goals:
                with st.spinner():
                    st.session_state.profile = update_personal_info(profile, "goals", goals=goals)
                    st.success('Goals updated')
            else:
                st.warning("Please select at least one goal.")

def get_macros(profile, goals):
    """
    Placeholder for generating macros.
    Replace with actual AI call or calculations later.
    """
    goal = goals[0] if goals else "general fitness"

    result = calorie_calculator_tool(
        weight_kg=profile["weight"],
        height_cm=profile["height"],
        age=profile["age"],
        gender=profile["gender"],
        goal=goal
    )

    return calorie_calculator_tool(profile, goals)
    

@st.fragment()
def macros():
    profile = st.session_state.profile
    nutrition = st.container(border=True)
    nutrition.header("Macros")
    if nutrition.button("Generate with AI"):
        result = get_macros(profile.get("general"), profile.get("goals"))
        profile["nutrition"] = result
        nutrition.success("AI has generated the results.")
    
    with nutrition.form("nutrition_form", border=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            calories = st.number_input("Calories", min_value=0, step=1, value=profile["nutrition"].get("calories", 0),)
        with col2:
            protein = st.number_input("Protein", min_value=0, step=1, value=profile["nutrition"].get("protein", 0),)
        with col3:
            fat = st.number_input("Fat", min_value=0, step=1, value=profile["nutrition"].get("fat", 0),)
        with col4:
            carbs = st.number_input("Carbs", min_value=0, step=1, value=profile["nutrition"].get("carbs", 0),)

        if st.form_submit_button("Save"):
            with st.spinner():
                st.session_state.profile = update_personal_info(profile, "nutrition", 
                                                                    protein=protein, 
                                                                    calories=calories,
                                                                    fat=fat,
                                                                    carbs=carbs
                                                                    )
                st.success("Information saved ")


@st.fragment()
def notes():
    st.subheader("Notes: ")
    user_notes = st.session_state.notes

    for i, note in enumerate(st.session_state.notes):
        cols = st.columns([5,1])
        with cols[0]:
            st.text(note.get("text"))
        with cols[1]:
            note_id = note.get("_id", i)
            if st.button("Delete", key=f"delete-{note_id}"):
                delete_note(note.get("_id"))
                st.session_state.notes.pop(i)
                st.rerun()

    #unique key using profile id
    profile_id = st.session_state.profile_id
    new_note = st.text_input("Add a new note: ", key=f"new-note-input-{profile_id}")

    if st.button("Add Note", key=f"add-note-button-{profile_id}"):
        if new_note:
            note = add_note(new_note, st.session_state.profile_id)
            st.session_state.notes.append(note)
            st.rerun()

    return user_notes

@st.fragment()
def food_image_uploader():
    st.header("Image-Based Food Recognition")
    uploaded_file = st.file_uploader("Upload a food photo (jpg, png, jpeg)", type=["jpg","jpeg","png"])

    if uploaded_file:
        with open("temp_uploaded_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image("temp_uploaded_image.jpg", caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Identifying food..."):
                food_name = identify_food_image("temp_uploaded_image.jpg")
                st.success("Food Analyzed!")
                st.write("### Food:", food_name)

                #Extract main food keyword
                keyword = extract_food_keyword(food_name)
                st.write("**Key Food**:", keyword)

                #Get nutrition data from keyword
                with st.spinner("Downloading nutritional info..."):
                    nutrition_result = nutrition_from_food(keyword)

                if "error" in nutrition_result:
                    st.error(nutrition_result["error"])
                else:
                    st.write("### Nutrition Facts")
                    st.write(f"**Calories:** {nutrition_result['nutrition'].get('calories', 'N/A')}" )
                    st.write(f"**Protein:** {nutrition_result['nutrition'].get('protein', 'N/A')}" )
                    st.write(f"**Fat:** {nutrition_result['nutrition'].get('fat', 'N/A')}" )
                    st.write(f"**Carbs:** {nutrition_result['nutrition'].get('carbs', 'N/A')}" )


@st.fragment()
def ask_ai_func(user_notes=None):
    st.subheader('Ask the AI Nutritionist')
    user_question = st.text_input("Ask AI a question: ")
    if st.button("Ask AI"):
        with st.spinner():
            profile = st.session_state.profile

            #combine general info + goals into one dict for the agent
            profile_input = {
                "weight_kg": profile["general"]["weight"],
                "height_cm": profile["general"]["height"],
                "age": profile["general"]["age"],
                "activity_level": profile["general"]["activity_level"],
                "goals": profile.get("goals", []),
                "notes": [note["text"] for note in user_notes] if user_notes else []
            }

            result = ask_ai(profile_input, user_question)

            if isinstance(result, dict) and "error" in result:
                st.error(f"Agent Failed: {result['error']}")
                st.write("Raw Output:", result["raw_output"])
            else:
                st.success("Feedback from your Nutritional Ai Agent:")
                st.write("### Diet Plan:", result.diet_plan)
                st.write("### Summary:", result.summary)
                st.write("### Meal Recommendations:", result.meal_recommendations)
                st.write("### Foods to Focus on:", ",".join(result.foods))
                st.write("### Tools Used:", ",".join(result.tools_used))



def forms():
    # is profile loaded in our state? if not, then go get it, if we get it and it doesn't exist, 
    # it means we don't have one and must create one
    if "profile" not in st.session_state:
        profile_id = 1

        #Force delete old/broken profile
        #personal_data_collection.delete_one({"_id": profile_id})

        #re-check if it exists and create fresh if needed
        profile = get_profile(profile_id)
        if not profile:
            profile_id, profile = create_profile(profile_id)

        st.session_state.profile = profile
        st.session_state.profile_id = profile_id

    if "notes" not in st.session_state:
        st.session_state.notes = get_notes(st.session_state.profile_id)

    personal_data_form()
    goals_form()
    macros()
    #notes()
    user_notes = notes()
    ask_ai_func(user_notes=user_notes)
    food_image_uploader()


if __name__ == "__main__":
    forms()