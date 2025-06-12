# HR Candidate Search App for South Africa
#
# This script creates a web-based GUI using Gradio that allows you to find
# potential job candidates in South Africa. It uses Google's Gemini API
# to generate realistic candidate profiles based on your search criteria.
#
# --- SETUP ---
#
# 1. Install necessary libraries:
#    pip install gradio google-generativeai pandas
#
# 2. Get your Gemini API Key:
#    - Go to Google AI Studio: https://aistudio.google.com/
#    - Click "Get API key" and create a new key.
#
# 3. Add your API Key as an environment variable named "GEMINI_API_KEY".
#    Alternatively, you can replace the placeholder in the script directly.
#
# 4. Run the script from your terminal:
#    python app.py
#
# 5. Open the local URL provided by Gradio in your browser.

import gradio as gr
import google.generativeai as genai
import os
import datetime
import pandas as pd
import io

# --- CONFIGURATION ---
# IMPORTANT: It's best practice to set the API key as an environment variable
# for security. The script will try to read it from there first.
# If you must, you can paste it directly, replacing the placeholder.
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAA9A3YI6qEBlXqCoTIbyF5lYDW234qgno")
    if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        print("WARNING: GEMINI_API_KEY environment variable not set. Please configure your API key.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
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
    # --- Input Validation ---
    if not all([job_title, skills, location]):
        return "## ⚠ Please fill in all fields before searching.", None

    if GEMINI_API_KEY in ["YOUR_GEMINI_API_KEY_HERE", "DISABLED"]:
        return "## ⛔ ERROR: Gemini API Key Not Configured\n\nPlease add your Gemini API key to the Python script or set it as an environment variable to enable searching.", None

    # --- Prompt Engineering ---
    sa_job_sites = [
        "linkedin.com/in/", "pnet.co.za", "careers24.com",
        "careerjunction.co.za", "za.indeed.com", "gumtree.co.za/s-jobs",
        "executiveplacements.com"
    ]

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
        # --- API Call ---
        # UPDATED: Changed model name to a current, valid one.
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        csv_data = response.text

        # --- Data Cleaning & Processing ---
        # Sometimes the model might wrap the output in markdown fences (```csv...```)
        if csv_data.strip().startswith("```csv"):
            csv_data = csv_data.strip()[6:-3].strip()
        
        # Create a temporary file to save the CSV
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_search_{timestamp}.csv"
        
        # Use pandas to read the CSV string and convert it to a markdown table
        df = pd.read_csv(io.StringIO(csv_data))
        markdown_table = df.to_markdown(index=False)

        # Save the dataframe to the CSV file
        df.to_csv(filename, index=False)

        # --- Return Results ---
        results_header = f"## Candidates for {job_title} in {location}"
        return f"{results_header}\n\n{markdown_table}", filename

    except Exception as e:
        error_message = f"## 💥 An error occurred\n\n**Details:**\n`{str(e)}`\n\n**Suggestion:**\nThis might be an issue with the API response or your API key. Please check your key and try again. If the problem persists, the model might have returned an unexpected format."
        return error_message, None

# --- GRADIO USER INTERFACE ---

# Custom CSS for a cleaner look
css = """
body { font-family: 'Inter', sans-serif; }
.gradio-container { max-width: 960px !important; margin: auto !important; }
footer { display: none !important; }
#results_header { text-align: center; }
"""

# Define the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), css=css) as demo:
    gr.Markdown("# 🇿🇦 HR Candidate Search")
    gr.Markdown("Find fictional ideal candidates for any role in South Africa using AI. Enter a job title, required skills, and a location to generate a list of potential profiles.")

    with gr.Row():
        with gr.Column(scale=2):
            job_title_input = gr.Textbox(label="Job Title", placeholder="e.g., Python Developer")
            skills_input = gr.Textbox(label="Key Skills", placeholder="e.g., Django, FastAPI, PostgreSQL, AWS")
            location_input = gr.Textbox(label="Location", placeholder="e.g., Cape Town, Western Cape")
    
    search_button = gr.Button("🔍 Search for Candidates", variant="primary")

    gr.Markdown("---")
    gr.Markdown("## 📄 Results", elem_id="results_header")
    
    # Outputs
    results_output = gr.Markdown(label="Candidate Profiles")
    download_link = gr.File(label="Download Results as CSV")

    # Define the button's click action
    search_button.click(
        fn=generate_candidates,
        inputs=[job_title_input, skills_input, location_input],
        outputs=[results_output, download_link]
    )
    
    gr.Examples(
        examples=[
            ["Data Scientist", "Python, Scikit-learn, TensorFlow, SQL", "Johannesburg"],
            ["UX/UI Designer", "Figma, Adobe XD, User Research, Prototyping", "Stellenbosch"],
            ["Digital Marketing Manager", "SEO, SEM, Google Analytics, Social Media Advertising", "Durban"]
        ],
        inputs=[job_title_input, skills_input, location_input]
    )

# --- LAUNCH THE APP ---

if __name__ == "__main__":
    demo.launch()
