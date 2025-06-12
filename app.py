# HR Candidate Search App for South Africa
#
# This script creates a web-based GUI using Gradio that allows you to find
# potential job candidates in South Africa. It uses Google's Gemini API
# to generate realistic candidate profiles based on your search criteria.
#
# --- SETUP ---
#
# 1. Install necessary libraries:
#    pip install gradio google-generativeai
#
# 2. Get your Gemini API Key:
#    - Go to Google AI Studio: https://aistudio.google.com/
#    - Click "Get API key" and create a new key.
#
# 3. Add your API Key below:
#    - Replace "YOUR_GEMINI_API_KEY" with your actual key.
#
# 4. Run the script from your terminal:
#    python your_app_name.py
#
# 5. Open the local URL provided by Gradio in your browser.

import gradio as gr
import google.generativeai as genai
import os
import datetime

# --- CONFIGURATION ---
# IMPORTANT: Replace with your actual Gemini API Key
try:
    # It's best practice to set the API key as an environment variable
    # for security, but you can paste it directly here for simplicity.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAA9A3YI6qEBlXqCoTIbyF5lYDW234qgno")
    genai.configure(api_key=GEMINI_API_KEY)
except AttributeError:
    print("Please provide your Gemini API key.")
    # This will prevent the app from crashing if the key is not provided.
    GEMINI_API_KEY = "DISABLED"


# --- CORE APPLICATION LOGIC ---

def generate_candidates(job_title, skills, location):
    """
    Uses the Gemini API to generate a list of fictional, ideal candidates.

    Args:
        job_title (str): The job role to search for.
        skills (str): Key skills or qualifications.
        location (str): The desired city or province in South Africa.

    Returns:
        A tuple containing:
        - A markdown-formatted string of the results.
        - The filepath to a downloadable CSV file of the results.
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY" or GEMINI_API_KEY == "DISABLED":
        return "## ERROR: Gemini API Key Not Configured\n\nPlease add your Gemini API key to the Python script to enable searching.", None

    # List of top South African job portals to base the search on.
    sa_job_sites = [
        "linkedin.com/in/",
        "pnet.co.za",
        "careers24.com",
        "careerjunction.co.za",
        "za.indeed.com",
        "gumtree.co.za/s-jobs",
        "executiveplacements.com"
    ]

    # The prompt for the Gemini model.
    # It instructs the model to act as an HR specialist and generate
    # plausible candidates in a specific format (CSV).
    prompt = f"""
    Act as an expert HR Recruitment Specialist for the South African market.
    Your task is to generate a list of 10 fictional, but highly plausible, candidate profiles who are ideal matches for the following role.
    Base these profiles on the kind of data you would typically find on top South African job sites like {', '.join(sa_job_sites)}.

    *Job Role:* {job_title}
    *Required Skills:* {skills}
    *Location:* {location}, South Africa

    Please generate a list of candidates. For each candidate, create a realistic name, a current job title, a primary location, a 2-sentence summary of their experience, and a list of 3-5 key skills.

    *IMPORTANT INSTRUCTION:* Format the entire output as a CSV (Comma-Separated Values) string ONLY, with no other text or explanation.
    The header row must be: "Full Name","Current Role","Location","Key Skills","Profile Summary","Source Profile URL"
    For the "Source Profile URL", create a realistic-looking but fake URL from one of the listed job sites.
    """

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-pro')

        # Generate content
        response = model.generate_content(prompt)
        csv_data = response.text

        # Clean the response to ensure it's valid CSV
        # Sometimes the model might wrap the output in markdown fences (csv ... )
        cleaned_csv = csv_data.strip().replace("csv", "").replace("", "").strip()

        # --- Create a downloadable CSV file ---
        # C