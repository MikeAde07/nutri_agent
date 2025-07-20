import streamlit as st
from profiles import create_profile, get_notes, get_profile 
from form_submit import update_personal_info, add_note, delete_note
from db import personal_data_collection

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


if __name__ == "__main__":
    forms()