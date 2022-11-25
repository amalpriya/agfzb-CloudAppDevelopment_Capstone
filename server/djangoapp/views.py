from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf,get_dealer_reviews_from_cf,post_request,get_dealer_details_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request,'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contactus(request):
    return render(request,'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('djangoapp:index')
        else:
            context['Message'] = "Invalid username/password"
            return render(request,'djangoapp/index.html',context)
    else:
        return render(request,'djangoapp/index.html',context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request,'djangoapp/registration.html',context)
    elif request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["psw"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is a new user",format(username))
        if not user_exist:
            user = User.objects.create_user(username=username,password=password,first_name=firstname,last_name=lastname)
            login(request,user)
            return redirect('djangoapp:index')
        else:
            context['Message'] = "User already exists"
            return render(request,'djangoapp/registration.html',context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        #URL corresponds to IBM Cloud Function Actions
        url = "https://au-syd.functions.appdomain.cloud/api/v1/web/aa23bdda-7506-4bbe-a3d1-7565a57bc851/dealership-package/get-dealerships"
        dealerships = get_dealers_from_cf(url)
        #dealer_names = ''.join([dealer.short_name for dealer in dealerships])
        #return HttpResponse(dealer_names)
        context["dealers"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context={}
    if request.method == "GET":
        # URL corresponds to IBM Cloud Function Actions
        review_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/aa23bdda-7506-4bbe-a3d1-7565a57bc851/review_package/get_reviews_for_dealership.py"
        dealer_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/aa23bdda-7506-4bbe-a3d1-7565a57bc851/dealership-package/get_details_for_dealership"
        reviews_list = get_dealer_reviews_from_cf(review_url,dealer_id)
        try:
            if "message" in reviews_list[0]:
                context["message"]="No reviews found"
        except:
            context["reviews_list"] = reviews_list
        dealer_details = get_dealer_details_from_cf(dealer_url, dealer_id)
        context["dealer_details"] = dealer_details
        return render(request,'djangoapp/dealer_details.html',context)
        

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context={}
    review={}
    json_payload={}
    user = request.user
    if user:
        if request.method=="GET":
            dealer_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/aa23bdda-7506-4bbe-a3d1-7565a57bc851/dealership-package/get_details_for_dealership"
            dealer_details = get_dealer_details_from_cf(dealer_url, dealer_id)
            cars = CarModel.objects.filter(dealerId=dealer_id)
            context["cars"] = cars
            context["dealer"]=dealer_details
            return render(request,'djangoapp/add_review.html',context)
        if request.method == "POST":
            url="https://au-syd.functions.appdomain.cloud/api/v1/web/aa23bdda-7506-4bbe-a3d1-7565a57bc851/review_package/post_review"
            review["dealership"] = dealer_id
            review["name"] = user.first_name
            review["purchase"] = (request.POST["purchasecheck"] == "on" )
            review["review"] = request.POST["content"]
            review["purchase_date"] = request.POST["purchasedate"]
            car_details= request.POST["car"]
            car_info = car_details.split('-')
            review["car_make"] = car_info[0]
            review["car_model"] = car_info[1]
            review["car_year"] = car_info[2]
            review["id"] = user.first_name+car_details+str(random.randint(200,1000))
            review["time"]=datetime.utcnow().isoformat()
            json_payload["review"] = review
            response=post_request(url, json_payload)
            return redirect("djangoapp:dealer_details",dealer_id=dealer_id)


