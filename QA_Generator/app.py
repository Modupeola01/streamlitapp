import streamlit as st
import json
from logic_template import openai_api_GPT4_st
import base64
from googleapiclient.discovery import build
from linkedin_api import Linkedin
from file_utils import *

logo = "images/creospan_logo_standard2.png"
st.image(logo, use_column_width=True)

st.title("Hello Creospan Team,")

st.markdown("App Description : The Automated Candidate Choice tool is a game-changing solution designed to revolutionize the candidate selection process for businesses. Leveraging advanced algorithms and machine learning techniques, this tool offers an efficient and data-driven approach to identify the best candidates for a job opening.")


# Create an input field for the prompt
job_des = st.file_uploader("Upload a Job Description")

# Create a field to upload a file
resume = st.file_uploader("Upload a Resume")

# Create an input field for the LinkedIn username
user = st.text_input("Enter LinkedIn Username")

if st.button("Generate All"):
    if (resume is not None):
        resume_text = check_file_extension(resume, st)
    if (job_des is not None):
        job_text = check_file_extension(job_des, st)
    
    api = Linkedin('feedbacksender335@gmail.com', st.secrets["LINKEDIN_PASS"])
    if (user != ""):
        profile = api.get_profile(user)
        profile_formatted = json.dumps(profile, indent=4)
    else:
        profile_formatted = ""

    prompts = get_prompts(resume_text, job_text, profile_formatted)

    final = ""

    for i in range(6):
        if i == 4 and user == "":
            continue

        final += options[i] + ":\n"
        prompt = prompts[i]

        # Call the openai_api_GPT4_st function with the prompt as an argument
        response = openai_api_GPT4_st(prompt)

        # Convert the dictionary response to a string
        response_string = json.dumps(response)

        # Parse JSON string into a dictionary
        data = json.loads(response_string)

        # Access and organize each element
        id_value = data['id']
        object_value = data['object']
        created_value = data['created']
        model_value = data['model']
        usage_value = data['usage']
        choices_value = data['choices']
        role_value = data['choices'][0]['message']['role']
        content_value = data['choices'][0]['message']['content']

        # Display the organized elements
        # st.write("ID:", id_value)
        #st.write("Object:", object_value)
        # st.write("Created:", created_value)
        # st.write("Model:", model_value)
        #st.write("Usage:", usage_value)
        #st.write("Choices:", choices_value)
        # st.write("Role:",role_value)
        questions = content_value.split("----------")
        j = 1
        for q in questions:
            q = q.replace("Look for", "\nLook for")
            q = q.replace("Answer:", "\nAnswer:")
            st.write(q)
            st.text_area(options[i] + " " + str(j) + " Notes")
            j += 1
        final += questions[0] + "\n\n"  
    st.download_button(
        label="Download File",
        data = final,
        file_name = "output",
    )

# st.header("Feedback")
# feedback = st.text_area("Please provide feedback on this app here. We would love to hear your thoughts!")
# if st.button("Send"):
#     st.write("Thank you for your feedback!")
#     creds = authenticate()
#     service = build('gmail', 'v1', credentials=creds)
#     message = {
#         'raw': base64.urlsafe_b64encode(
#             f'From: feedbacksender335@gmail.com\n'
#             f'To: ag7@uchicago.edu\n'
#             f'Subject: New Feedback!\n\n'
#             f'{feedback}'.encode()
#             ).decode()
#     }
#     sent_message = service.users().messages().send(userId='me', body=message).execute()
