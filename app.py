import streamlit as st
import json
from gtts import gTTS
from io import BytesIO
from voice_utils import recognize_speech, speak_text
from chefbot_logic import suggest_dishes

# App title
st.set_page_config(page_title="ChefBot", page_icon="🍳", layout="centered")
st.title("👩‍🍳 ChefBot – Your AI Kitchen Assistant")

# Sidebar section
st.sidebar.header("🍽️ Choose Input Type")
input_type = st.sidebar.radio("Select how you want to talk to ChefBot:", ["Text", "Voice"])
voice_mode = st.sidebar.checkbox("Enable Voice Output 🔊", value=True)

# Load recipes
with open("data/recipes.json", "r") as f:
    recipes = json.load(f)

# Main section
st.write("Welcome to **ChefBot!** Tell me what ingredients you have, and I’ll find recipes for you.")

# -----------------------
# Get user input
# -----------------------
if input_type == "Text":
    ingredients_input = st.text_input("Enter the ingredients you have (comma separated):")
else:
    st.write("🎤 Click the button below and speak your ingredients...")
    if st.button("Start Recording"):
        ingredients_input = recognize_speech()
        if ingredients_input:
            st.success(f"You said: {ingredients_input}")
        else:
            st.warning("Sorry, I couldn’t hear you. Try again.")
    else:
        ingredients_input = ""

# -----------------------
# Suggest dishes
# -----------------------
if st.button("Get Recipes 🍲") and ingredients_input:
    ingredients = [i.strip().lower() for i in ingredients_input.split(",")]
    possible_dishes = suggest_dishes(recipes, ingredients)

    if possible_dishes:
        st.session_state.possible_dishes = possible_dishes
        st.session_state.selected_dish = None
        st.session_state.current_step = 0
        st.success("Here are some dishes you can make:")
        for dish in possible_dishes:
            time = dish.get("time_minutes", "N/A")
            st.write(f"- {dish['name']} ({time} mins)")


        # Suggest one "best" dish (quick + impressive)
        best_dish = sorted(possible_dishes, key=lambda x: (x["time_minutes"], x["type"] != "impress"))[0]
        st.session_state.selected_dish = best_dish
        st.subheader(f"⭐ Recommended Dish: {best_dish['name']}")
    else:
        st.warning("Sorry, I couldn’t find any dish with those ingredients 😢")

# -----------------------
# Show chosen recipe
# -----------------------
if "selected_dish" in st.session_state and st.session_state.selected_dish:
    dish = st.session_state.selected_dish
    st.divider()
    st.header(f"🍛 {dish['name']}")
    st.write(f"⏱️ Estimated time: {dish['time_minutes']} mins")
    st.write("### Ingredients:")
    st.write(", ".join(dish["ingredients"]))

    # Step navigation logic
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    steps = dish["steps"]
    st.write(f"### Step {st.session_state.current_step + 1}:")
    st.info(steps[st.session_state.current_step])

    # Buttons for step control
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous Step") and st.session_state.current_step > 0:
            st.session_state.current_step -= 1
    with col2:
        if st.button("🔁 Repeat Step"):
            pass  # just replays same step
    with col3:
        if st.button("➡️ Next Step") and st.session_state.current_step < len(steps) - 1:
            st.session_state.current_step += 1

    # Voice output for step (optional)
    if voice_mode:
        if st.button("🔊 Read This Step Aloud"):
            speak_text(steps[st.session_state.current_step])
