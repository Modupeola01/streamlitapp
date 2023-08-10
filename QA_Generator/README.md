# Creospan's QA Generator
Demo: https://arjun2garg-qagenerator-app-io3kti.streamlit.app/

*![Project Name screenshot](screenshot will go here)*

## Introduction
Creospan's QA Generator is a powerful tool that simplifies the employee recruitment process. Built using Python, this application can be run locally or deployed as a web app. The QA Generator analyzes resumes and job description to evaluate the resume on different metrics and generate tailored interview questions and sample answers. With an easy-to-use web interface, users can upload information and recieve results in real-time.

## Value Proposition Thesis
Our solution is a highly adaptable and extendable QA generator that can be customized to the needs of any job opening and provide a comprehensive assistant for the entire recruitment process. It is designed with a microservices-first approach, making it easy to add new features such as user authentication, transaction history, and more. This system can help businesses streamline the recruitment process to save time and resources, as well as decreasing the barrier to becoming a qualified interviewer. It's an all-in-one tool for candidate screening.

## Possible Go-To-Market Strategies
### Go-to-Market Strategy 1: Client Facing SaaS Model
Launch the QA Generator as a web application where users can subscribe on a monthly or yearly basis to use your service, or choose to pay per use. They can input a resume job description, and our service will evaluate the resume, as well as generate interview questions and answers. The target audience would be recruiters who wish to streamline the recruitment process. This is a straightforward approach, easily measurable by user acquisition, engagement and subscription revenue.

### Go-to-Market Strategy 2: Candidate Facing SaaS Model
Launch the QA Generator as a web application where users can subscribe on a monthly or yearly basis to use your service. They can input their resume and a description for a job they are applying to, and our service will evaluate the strength of their resume, as well as interview questions and answers to prepare. This would change the target audience from recruiters to job-seekers, which could provide value in another way. This is a straightforward approach, easily measurable by user acquisition, engagement and subscription revenue.

### Go-to-Market Strategy 3: Custom Solutions Provider
Instead of a standalone web app, we could offer our service as a custom solutions provider. Customers would describe what they need, and we would provide them a fully functioning recruitment assistant. We could charge a fee for the initial setup, and then a maintenance fee for keeping the program updated and functional. This approach will be more resource-intensive but might attract larger businesses and lead to bigger deals.

### Go-to-Market Strategy 4: Candidate Recruiter
Instead of a standalone web app, we could offer to take over the recruitment process for a client. Customers would describe what they need, and we would use this app internally to find qualified candidates for the client. We would charge a variable fee that depends on the amount of candidates and the difficulty of acquiring those candidates, depending on the state of the market. This approach would be the most resource-intensive, but could return huge dividends if we are able to beat the market standard for talent acquisition.

## Getting Started
### Prerequisites
To run the QA Generator locally, you will need:

Python 3.8 or higher
pip (Python package installer)

## Installation
Clone the GitHub repository or download the source code as a ZIP file:
git clone https://github.com/arjun2garg/QAGenerator.git

Navigate to the project directory:
cd QAGenerator

Install the required Python packages:
pip install -r requirements.txt

## Running the QA Generator
To run the scraper locally, use the following command:
streamlit run app.py
This will open the app in your web browser, where you can interact with the UI.

Alternatively, you can access the deployed web app at https://arjun2garg-qagenerator-app-io3kti.streamlit.app/.

# Code Overview
The app.py file uses Streamlit to create a web app that allows users to input their information and select what they want the bot to do. When they click 'Submit', the app sends an engineered query to OpenAI's GPT4 API in order to perform the selected action. Once GPT4 has come up with a response, it is displayed on the app for the user to see.

## Troubleshooting and Common Issues
#### LinkedIn Comparison
- Due to problems with the API, the LinkedIn comparison tool may not be working in the deployed app. It should still work locally.
#### Feedback Form
- Due to privacy issues, the feedback form may not be working on the deployed app. It should still work locally.

### Future Enhancements
- Integration with PrivateGPT which allows it to craft better responses based on sample resumes and job descriptions.
- Integration with VoiceGPT in order to record interview responses in real-time and open up the option for tools like plagiarism detectors or candidate answer evaluation.
- Decreasing the response time.

### Contributing
We welcome contributions from the community! To contribute, please follow these steps:
- Fork the repository on GitHub.
- Create a new branch for your changes.
- Make your changes and commit them to your branch.
- Create a pull request with a description of your changes.
- We will review your pull request and provide feedback. Once your changes are approved, they will be merged into the main repository.

### Support
If you have any questions, issues, or suggestions for improvement, please feel free to open an issue on the GitHub repository or contact the maintainers directly.

We appreciate your interest in Creospan's QA Generator and look forward to helping you make the most of this powerful tool!
