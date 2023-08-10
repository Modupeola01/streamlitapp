import streamlit as st
import os
import shutil
import time
import threading
import pandas as pd
import json
import requests
from logic_template import openai_api_GPT4_st
from PyPDF2 import PdfReader
import re
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import requests
from linkedin_api import Linkedin
from file_utils import check_file_extension
# from bs4 import BeautifulSoup
# from sumy.parsers.html import HtmlParser
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lsa import LsaSummarizer

def parse_pdf(file):
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        output.append(text)

    return output

#Scopes required for accessing Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    """Authenticate with Gmail API using OAuth 2.0"""
    creds = None

    # Load or create credentials token file
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid token available, authenticate user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

logo = "images/creospan_logo_standard2.png"
st.image(logo, use_column_width=True)

st.title("Hello Creospan Team,")

st.markdown("App Description : The Automated Candidate Choice tool is a game-changing solution designed to revolutionize the candidate selection process for businesses. Leveraging advanced algorithms and machine learning techniques, this tool offers an efficient and data-driven approach to identify the best candidates for a job opening.")

# Create an input field for the job description
job_description = st.text_area("Enter a Job Description")
st.text("OR")
uploaded_file_Jd = st.file_uploader("Upload Job Description", key="jobDescription")

# Create an input field for the resume
resume = st.text_area("Enter a Resume")
st.text("OR")
uploaded_file_Rs = st.file_uploader("Upload Resume", key="resume")

# Create an input field for the LinkedIn username
user = st.text_input("Enter LinkedIn Username")

file_contents_Jd = ""
if uploaded_file_Jd is not None:
    # Check the file extension
    file_contents_Jd = check_file_extension(uploaded_file_Jd, st)

file_contents_Rs = ""
if uploaded_file_Rs is not None:
    # Check the file extension
    file_contents_Rs = check_file_extension(uploaded_file_Rs, st)   

# Combine uploaded file text with prompts
if file_contents_Jd:
    job_description += " " + file_contents_Jd
if file_contents_Rs:
    resume += " " + file_contents_Rs

# Define the options for the dropdown
options = [
    "General Question",
    "Technical Question",
    "Work Experience Question",
    "Leadership Question",
    "Small Talk Question",
    "General Score",
    "Education Score",
    "Experience Score",
    "Fit Score",
    "LinkedIn Comparison"
]

# Create the dropdown list
selected_option = st.selectbox("Select an option", options)

# Define the response_string variable outside the if block
response_string = ""

# Button for submission
if st.button("Submit"):
    # if (resume is not None):
    #     resume_text = parse_pdf(resume)
    
    
    # Create prompt based on selected option
    if (selected_option == options[0]):
        prompt = f"I want you to act as an interviewer for a job opening with the following job description:\n\n{job_description}\n\n Here is the candidate's resume that you are interviewing:\n\n{resume_text}\n\nYou should be more conversational and less interrogative in your interview. What is a question that you will ask in your interview? What are the important things you will look for in the candidate's answer?"    
    elif (selected_option == options[1]):
        prompt = f"I want you to act as an interviewer for a job opening with the following job description:\n\n{job_description}\n\n Here is the candidate's resume that you are interviewing:\n\n{resume_text}\n\nYou should be more conversational and less interrogative in your interview. What is a technical question that you will ask in your interview? What are the important things you will look for in the candidate's answer?"    
    elif (selected_option == options[2]):
        prompt = f"I want you to act as an interviewer for a job opening with the following job description:\n\n{job_description}\n\n Here is the candidate's resume that you are interviewing:\n\n{resume_text}\n\nYou should be more conversational and less interrogative in your interview. What is a question about the candidate's work experience that you will ask in your interview? What are the important things you will look for in the candidate's answer?"    
    elif (selected_option == options[3]):
        prompt = f"I want you to act as an interviewer for a job opening with the following job description:\n\n{job_description}\n\n Here is the candidate's resume that you are interviewing:\n\n{resume_text}\n\nYou should be more conversational and less interrogative in your interview. What is a question about the candidate's leadership skills that you will ask in your interview? What are the important things you will look for in the candidate's answer?"    
    elif (selected_option == options[4]):
        prompt = f"I want you to act as an interviewer for a job opening with the following job description:\n\n{job_description}\n\n Here is the candidate's resume that you are interviewing:\n\n{resume_text}\n\nYou should be more conversational and less interrogative in your interview. What is a small talk question that you will ask in your interview to make the candidate feel more at ease?"    
    elif (selected_option == options[5]):
        prompt = f"I am interviewing a candidate for the following job description:\n\n{job_description}\n\nHere is the candidate's resume:\n\n{resume_text}\n\nCan you score this candidate from 1-10 for the categories of education level, work experience, job fit, communication skills, and technical skills? If they are underqualified for aspects of the job, they should score lower than a 5"
    elif (selected_option == options[6]):
        prompt = f"I am interviewing a candidate for the following job description:\n\n{job_description}\n\nHere is the candidate's resume:\n\n{resume_text}\n\nCan you score this candidate from 1-10 for their level of education based on the following scale: 1 = No education, 4 = High school, 6 = Some college, 7 = Associate's degree, 8 = Bachelor's degree, 9 = Master's degree, 10 = Doctorate degree? Note that if their degree is still in progress, they should not be scored for that degree."
    elif (selected_option == options[7]):
        prompt = f"I am interviewing a candidate for the following job description:\n\n{job_description}\n\nHere is the candidate's resume:\n\n{resume_text}\n\nCan you score this candidate from 1-10 for their work experience? If they satisfy the requirements in the job description they should recieve at least a 7. Then determine their score based on if they have more or less experience than required. Make sure to consider both the relevancy and duration of their work experience."
    elif (selected_option == options[8]):
        prompt = f"I am interviewing a candidate for the following job description:\n\n{job_description}\n\nHere is the candidate's resume:\n\n{resume_text}\n\nCan you score this candidate from 1-10 for how well of a fit they are for the job? If they are underqualified, they should score lower than a 5"
    elif (selected_option == options[9]):
            api = Linkedin('feedbacksender335@gmail.com', st.secrets["LINKEDIN_PASS"])
            profile = api.get_profile(user)
            profile_formatted = json.dumps(profile, indent=4)
            prompt = f"I want you to act as a resume screener who is reviewing the following resume:\n\n{resume_text}\n\nHere is information from the candidate's LinkedIn profile:\n\n{profile_formatted}\n\nCan you point out any important discrepencies between the candidate's resume and LinkedIn profile, if they exist, that might point to the candidate's resume being inaccurate?"
    
    # Call the openai_api_GPT4_st function with the prompt as an argument
    response = openai_api_GPT4_st(prompt)

    # Convert the dictionary response to a string
    response_string = json.dumps(response)
    # st.write(response_string)

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
    questions = content_value.split("Question ")
    st.write(content_value.split("Question ")[0])

st.header("Feedback")
feedback = st.text_area("Please provide feedback on this app here. We would love to hear your thoughts!")
if st.button("Send"):
    st.write("Thank you for your feedback!")
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    message = {
        'raw': base64.urlsafe_b64encode(
            f'From: feedbacksender335@gmail.com\n'
            f'To: ag7@uchicago.edu\n'
            f'Subject: New Feedback!\n\n'
            f'{feedback}'.encode()
            ).decode()
    }
    sent_message = service.users().messages().send(userId='me', body=message).execute()

