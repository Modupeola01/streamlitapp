import csv
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import GoogleAuthError
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import stripe
import openai
from paypalrestsdk import Payment
import requests

load_dotenv()

# Optional environment variables to load in
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# stripe.api_key = os.environ.get("STRIPE_API_KEY")

# Deploy the updated code and check the logs to see if the environment variables are printed as expected. If the environment variables are still not set correctly, there might be an issue with the runtime environment.
# print("Environment variables:")
# print("GOOGLE_REDIRECT_URI:", os.environ.get("GOOGLE_REDIRECT_URI"))
# print("GOOGLE_CLIENT_ID:", os.environ.get("GOOGLE_CLIENT_ID"))
# print("GOOGLE_CLIENT_SECRET:", os.environ.get("GOOGLE_CLIENT_SECRET"))
# firebase_config = {
#     "apiKey": os.environ["FIREBASE_API_KEY"],
#     "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
#     "projectId": os.environ["FIREBASE_PROJECT_ID"],
#     "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
#     "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
#     "appId": os.environ["FIREBASE_APP_ID"],
#     "measurementId": os.environ["FIREBASE_MEASUREMENT_ID"]
# }
# openai_api_key = os.environ["OPENAI_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

## Functions for Payments
def create_payment_intent():
    try:
        payment_intent = stripe.Payment.Intent.create(
            amount=100,
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'}
        )
        session['paid'] = True
        return jsonify({'client_secret': payment_intent['client_secret']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def create_payment():
    payment_intent = stripe.PaymentIntent.create(
        amount=100,  # $1.00
        currency='usd',
    )
    return jsonify(clientSecret=payment_intent.client_secret)

def payment_success():
    session['paid'] = True
    print("Payment successful. Session 'paid' key set to:", session['paid'])
    return '', 204

def create_paypal_payment():
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        # "redirect_urls": {
        #     "return_url": "http://localhost:5000/payment-success",
        #     "cancel_url": "http://localhost:5000/payment-cancel"
        # },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "PROJECT_NAME Interaction",
                    "sku": "item",
                    "price": "1.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "1.00",
                "currency": "USD"
            },
            "description": "PROJECT_NAME Interaction"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        return jsonify({'error': 'Payment creation failed.'}), 400


def apply_promo_code():
    promo_code = request.form.get('promo_code')
    promo_codes = {
        'PROMO10': 0.1,
        'PROMO20': 0.2
    }
    discount = promo_codes.get(promo_code.upper(), 0)
    if discount > 0:
        return jsonify({'discount': discount})
    else:
        return jsonify({'error': 'Invalid promo code.'}), 400

def create_subscription():
    customer_id = request.form.get('customer_id')
    plan_id = request.form.get('plan_id')

    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'plan': plan_id
            }]
        )
        return jsonify({'subscription_id': subscription.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


## Functions for Authentication
def get_google_auth_flow():
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    project_id = os.environ.get('GOOGLE_PROJECT_ID')
    if redirect_uri != "https://storyspark.app/oauth2callback":
        print("expected GOOGLE_REDIRECT_URI of: https://storyspark.app/oauth2callback")

    # Test the variables are defined properly
    # print(f"Client ID: {client_id}")
    # print(f"Client Secret: {client_secret}")
    # print(f"Redirect URI: {redirect_uri}")
    flow = Flow.from_client_config(
        # {'web': {'client_id': client_id, 'storyspark-383601': 'your_project_id', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_secret': client_secret, 'redirect_uris': [redirect_uri]}},
        {'web': {'client_id': client_id, 'project_id': project_id, 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_secret': client_secret, 'redirect_uris': [redirect_uri]}},
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=redirect_uri
    )
    return flow

def get_user_info(credentials):
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        userinfo = service.userinfo().get().execute()
        return userinfo
    except HttpError as e:
        print(f"An error occurred: {e}")
        userinfo = None
    return userinfo

def login():
    google = get_google_auth_flow()
    auth_url, _ = google.authorization_url(access_type='offline')
    print("Generated auth_url:", auth_url)
    return redirect(auth_url)

def oauth2callback():
    print("Entered oauth2callback function")
    try:
        google = get_google_auth_flow()
        print("Request URL:", request.url)
        google.fetch_token(
            token_uri='https://oauth2.googleapis.com/token',
            authorization_response=request.url)
        print("Fetched token")
        session['credentials'] = google.credentials.to_json()
        # When you need to use the credentials later in the application, you can convert the JSON string back to a 'Credentials' object using the 'from_json()' method, like this:
        # credentials = Credentials.from_json(session['credentials'])
        print("Set session credentials")
        return redirect(url_for('index'))
    except GoogleAuthError as e:
        print(f"Error during authentication: {e}")
        return f"Error: {e}", 500


# Functions for interacting with OpenAI API using Streamlit
def openai_api_st(prompt):
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-codex/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "prompt": prompt,
            "max_tokens": 2000,
            "n": 1,
            "stop": None,
            "temperature": 0.8,
        },
    )
    return response.json()


def openai_api_GPT4_st(prompt):
    # Define your messages here
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "model": "gpt-4",  # Change the model to GPT-4
            "messages": messages,
            "max_tokens": 2000,
            "n": 1,
            "stop": None,
            "temperature": 0.8,
        },
    )
    return response.json()  # Return the JSON response




# Functions for interacting with OpenAI API
def openai_api():
    prompt = request.json["prompt"]
    response = requests.post(
        "https://api.openai.com/v1/engines/text-davinci-003/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "prompt": prompt,
            "max_tokens": 2000,
            "n": 1,
            "stop": None,
            "temperature": 0.8,
        },
    )
    return jsonify(response.json())

def openai_api_GPT4():
    messages = request.json["messages"]
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "model": "gpt-4",  # Change the model to GPT-4
            "messages": messages,
            "max_tokens": 2000,
            "n": 1,
            "stop": None,
            "temperature": 0.8,
        },
    )
    return jsonify(response.json())

def openai_api_GPT4_super():
    messages = request.json["messages"]
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "model": "gpt-4",  # Change the model to GPT-4
            "messages": messages,
            "max_tokens": 32000,
            "n": 1,
            "stop": None,
            "temperature": 0.8,
        },
    )
    return jsonify(response.json())


def main():
    pass

if __name__ == "__main__":
    main()
