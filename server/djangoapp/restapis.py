import os
import requests
import json
from dotenv import load_dotenv
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

load_dotenv()

NLU_API_KEY = os.getenv("NLU_API_KEY")
NLU_URL = os.getenv("NLU_URL")

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    
    json_obj = json_payload["review"]
    try:
        response = requests.post(url, json=json_obj, params=kwargs)
    except: 
        print("Something went wrong")

    print(response)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealers_by_state_from_cf method to get dealers by dealer state from a cloud function
def get_dealers_by_state_from_cf(url, state): 
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state)
    if json_result:
        # Get the list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_by_id_from_cf(url, dealerId):
    results = []

    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the list in JSON as dealers
        reviews = json_result["result"]
        # For each review object
        for review in reviews:
            # Create a DealerReview object with values in object
            try:
                review_obj = DealerReview(
                    name = review["name"], dealership = review["dealership"], 
                    review = review["review"], purchase = review["purchase"],
                    purchase_date = review["purchase_date"], car_make = review['car_make'],
                    car_model = review['car_model'], car_year= review['car_year'], sentiment = 'none'
                )
            except:
                review_obj = DealerReview(
                    name = review["name"], dealership = review["dealership"], 
                    review = review["review"], purchase = review["purchase"],
                    purchase_date = 'none', car_make = 'none',
                    car_model = 'none', car_year= 'none', sentiment = 'none'
                )

            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    authenticator = IAMAuthenticator(NLU_API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(NLU_URL)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(sentiment=SentimentOptions())
    ).get_result()
    print(json.dumps(response))
    sentiment_score = str(response["sentiment"]["document"]["score"])
    sentiment_label = response["sentiment"]["document"]["label"]
    print(sentiment_score)
    print(sentiment_label)
    sentimentresult = sentiment_label
    
    return sentimentresult
