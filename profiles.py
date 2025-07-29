from db import personal_data_collection, notes_collection


#returns a sample version of what we're going to be storing in our personal data collection from streamlit front end UI
def get_values(_id):
    return {
        "_id": _id,
        "general" : {
            "name": "",
            "age": 30,
            "weight": 60,
            "height": 165,
            "activity_level": "Moderately Active",
            "gender": "Male"
        },
        "goals": ["Muscle Gain"],
        "nutrition": {
            "calories" : 2000,
            "protein": 140,
            "fat": 20,
            "carbs": 100
        },
    }

def create_profile(_id):
    profile_values = get_values(_id)
    result = personal_data_collection.insert_one(profile_values)
    profile = personal_data_collection.find_one({"_id": result.inserted_id})
    return result.inserted_id, profile

# reference to this can be found in data stacks documentation. we have our id field and we're looking for any ids that equal that id.
def get_profile(_id):
    #print("DEBUG: Fetching profile for ID:", _id)
    return personal_data_collection.find_one({"_id": {"$eq": _id}})

#match user_id to _id. Allows us to get notes associated with profile. 
def get_notes(_id):
    return list(notes_collection.find({"user_id": {"$eq": _id}}))