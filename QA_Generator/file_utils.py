import os
import re
import docx
from PyPDF2 import PdfReader
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText

options = [
    "Behavioral Question",
    "Technical Question",
    "Job Description Comparison",
    "Attribute Score",
    "LinkedIn Comparison",
    "Resume Percentage",
]

def get_prompts(resume_text, job_text, profile_formatted):
    prompts = [
        f'''
        The goal of the  interviewer is to ask  questions that will determine whether the candidate actually has the skills that are needed for the job as described in the job description by utilizing the candidate’s resume as the source of capabilities, skills and experiences to validate.
        For an interviewer that doesn't have much experience, asking these types of questions based on the resume and job description is difficult.
        I want you to serve as a tool for these interviewers by generating interview questions that will provide the interviewer confidence that the candidate has the skills required to do the job as described in the job description.
        Here is a job description for an open position:

        {job_text}
        
        Here is a candidate's resume that is interviewing for this position:
        
        {resume_text}
        
        Can you generate 3 interview questions for the interviewer to ask the candidate considering the candidate’s experience as expressed through the resume that will help the interviewer determine whether the candidate is a good fit for the job? Can you also highlight the important things to look for in their answer.
        Keep in mind that each question should only ask for one thing at a time, to avoid a situation where the candidate selectively only answers one of the things you ask for. Also, the question should be specific to the candidate's resume.
        In between each question, include a line that is "----------"
        ''',

        f'''
        Here is a job description for an open position:

        {job_text}
        
        Here is a candidate's resume that is interviewing for this position:
        
        {resume_text}

        Identify what technical skills are in the job description that the candidate also claims to know based on their resume. Then, based on that, generate 5 close-ended, technical questions about those skills that determines whether they are qualified for the job. 
        Note that the questions should not be based on their experience (such as "Recall a time when...") but rather close-ended questions that have a definitive answer (such as "How would you _ in Python?"). Also provide what those answers are.
        The questions should be fairly difficult, to the level of professionals with 5-10 years of experience.
        In between each question, include a line that is "----------"
        ''',

        f'''
        Here is a job description for an open position:

        {job_text}
        
        Here is a candidate's resume that is interviewing for this position:
        
        {resume_text}

        Identify what skills, if any, are in the job description that are absent from the resume.
        ''',

        f"I am interviewing a candidate for the following job description:\n\n{job_text}\n\nHere is the candidate's resume:\n\n{resume_text}\n\nCan you score this candidate from 1-10 for the categories of education level, work experience, job fit, communication skills, and technical skills? If they are underqualified for aspects of the job, they should score lower than a 5",

        f"I want you to act as a resume screener who is reviewing the following resume:\n\n{resume_text}\n\nHere is information from the candidate's LinkedIn profile:\n\n{profile_formatted}\n\nCan you point out any important discrepencies between the candidate's resume and LinkedIn profile, if they exist, that might point to the candidate's resume being inaccurate?",

        f"Here is a candidate's resume:\n\n{resume_text}\n\nCan you determine the candidate's qualifications based on their resume by deciding what percent of each position they are. For example, someone's resume might indicate that they are 40% frontend developent, 30% machine learning, and 30% cloud engineering."
    ]
    return prompts

options = [
    "Behavioral Question",
    "Technical Question",
    "Job Description Comparison",
    "Attribute Score",
    "LinkedIn Comparison",
    "Resume Percentage",
]

supported_file_types = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt"
}

supported_file_types_list = [val for val in supported_file_types.values()]
def check_file_extension(uploaded_file, st):
    file_content = ""
    if uploaded_file.type == "application/pdf":
        file_content = parse_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_content = parse_docx(uploaded_file)
    elif uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/msword":
        st.error("File Type not supported: .doc")
        st.error("Please upload a .docx file")
    else:
        st.error("File Type not supported: " + uploaded_file.type)
        st.error("Supported file types are: " + (", ").join(supported_file_types_list))

    return file_content

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

def parse_docx(file):
    doc = docx.Document(file)
    paragraphs = [p.text for p in doc.paragraphs]
    text = '\n'.join(paragraphs)
    return text
        
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