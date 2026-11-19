import streamlit as st
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List
import json

# Configure Streamlit page
st.set_page_config(page_title="Bhawna: AI Travel Planner", page_icon="✈️", layout="centered")

st.title("✈️ Bhawna: AI Personalized Travel Itinerary Planner")
st.write("Tell us about your dream trip, and let Bhawna craft a custom, day-by-day schedule for you!")

# Sidebar for API Key & Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google Gemini API Key:", type="password")
    st.markdown("---")
    st.markdown("### About Bhawna")
    st.info("Bhawna uses Generative AI and structured schemas to build customized travel plans tailored to your exact pace and budget.")

if api_key:
    genai.configure(api_key=api_key)

    # Main Form Inputs
    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Destination City & Country", placeholder="e.g., Tokyo, Japan")
        duration = st.number_input("Number of Days", min_value=1, max_value=14, value=3)
    with col2:
        budget = st.selectbox("Budget Level", ["Budget-friendly", "Moderate / Mid-range", "Luxury"])
        travel_style = st.selectbox("Travel Style", ["Foodie & Culinary", "History & Culture", "Adventure & Outdoors", "Relaxed & Scenic", "Mixed / Balanced"])

    interests = st.text_input("Specific Interests or Must-See Places", placeholder="e.g., local street food, art museums, hiking")

    if st.button("Generate My Itinerary 🌍", type="primary"):
        if not destination:
            st.warning("Please enter a destination!")
        else:
            with st.spinner(f"Bhawna is crafting your {duration}-day trip to {destination}..."):
                
                # Define Pydantic schema to ensure structured output
                class Activity(BaseModel):
                    time_slot: str = Field(description="Morning, Afternoon, or Evening")
                    activity_name: str = Field(description="Name of the place or activity")
                    description: str = Field(description="Short description of what to do there")
                    estimated_cost: str = Field(description="Estimated cost category")

                class DayItinerary(BaseModel):
                    day_number: int
                    theme: str = Field(description="Theme for the day")
                    activities: List[Activity]

                class TravelPlan(BaseModel):
                    trip_title: str
                    overview: str
                    days: List[DayItinerary]
                    packing_tips: List[str]

                # Construct Prompt
                prompt = f"""
                You are Bhawna, an expert AI travel planner. Create a detailed {duration}-day personalized travel itinerary for {destination}.
                
                Parameters:
                - Budget: {budget}
                - Travel Style: {travel_style}
                - Specific Interests: {interests if interests else 'General highlights'}
                
                Return the response strictly adhering to the requested structured format.
                """

                try:
                    # Call Gemini model with structured output
                    model = genai.GenerativeModel("gemini-3.8-flash")
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "response_mime_type": "application/json",
                            "response_schema": TravelPlan,
                        },
                    )

                    # Parse and display result
                    plan_data = json.loads(response.text)

                    st.success("Your itinerary is ready!")
                    st.header(plan_data["trip_title"])
                    st.write(plan_data["overview"])

                    for day in plan_data["days"]:
                        with st.expander(f"Day {day['day_number']}: {day['theme']}", expanded=True):
                            for act in day["activities"]:
                                st.markdown(f"**🕒 {act['time_slot']} — {act['activity_name']}**")
                                st.write(act["description"])
                                st.caption(f"Estimated Cost: {act['estimated_cost']}")
                                st.divider()

                    st.subheader("🎒 Quick Packing Tips")
                    for tip in plan_data["packing_tips"]:
                        st.markdown(f"- {tip}")

                except Exception as e:
                    st.error(f"An error occurred while generating the itinerary: {e}")
else:
    st.warning("Please enter your Google Gemini API key in the sidebar to start building itineraries with Bhawna.")
