import requests
import json
from .models import CarDealer,DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url,**kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url,headers={'Content-Type':'application/json'},params=kwargs)
    except:
        print("Network Exception occured")
    status_code = response.status_code
    print("With Status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url,json_payload,**kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url,params=kwargs,json=json_payload)
    except:
        print("Network Exception occured")
    status_code=response.status_code
    print("With Status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data
    


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
    results=[]
    json_result = get_request(url)
    if (json_result):
        dealers=json_result["data"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                state=dealer_doc["state"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )
            results.append(dealer_obj)
    return results

def get_dealer_details_from_cf(url,dealerId):
    json_result = get_request(url,id=dealerId)
    if (json_result):
        dealer = json_result["data"][0]
        dealer_obj = CarDealer(
                address=dealer["address"],
                city=dealer["city"],
                full_name=dealer["full_name"],
                id=dealer["id"],
                lat=dealer["lat"],
                long=dealer["long"],
                short_name=dealer["short_name"],
                state=dealer["state"],
                st=dealer["st"],
                zip=dealer["zip"]
        )
    return dealer_obj
    

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    results = []
    try:
        json_result = get_request(url,id=dealerId)
        if (json_result):
            reviews = json_result["data"]
            for review in reviews:
                sentiment = analyze_review_sentiments(review["review"])
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=review["purchase_date"],
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    sentiment=sentiment.strip('\"'),
                    id=review["id"]
                )
                results.append(review_obj)
    except Exception as exception:
        results.append({"message":"No reviews yet"})
    return results
                

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(input_text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    authenticator = IAMAuthenticator("6TKoVyqekVrSmxQAPJDYCnixGhMBYKmWeHFR5ew4P7Ms")
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version="2022-11-24",
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url("https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/8808773e-17d9-41c9-a9cd-67ac4a9a8155")
    response=natural_language_understanding.analyze(
        text=input_text,
        features=Features(
            #sentiment=SentimentOptions(model="sentiment-analysis-en-v1")
            sentiment=SentimentOptions()
        ),
        language="en").get_result()
    return json.dumps(response["sentiment"]["document"]["label"],indent=2)



