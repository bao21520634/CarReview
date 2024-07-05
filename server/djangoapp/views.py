from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from dotenv import load_dotenv
from .models import CarModel
from . import restapis
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import os

load_dotenv()

WEB_ACTION_URL = os.getenv("WEB_ACTION_URL")

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request 
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.META.get('HTTP_REFERER').find('/djangoapp/login/') == -1:
                return redirect(request.META.get('HTTP_REFERER'))
            elif request.META.get('HTTP_REFERER').find('/djangoapp/login/') != -1:
                return redirect('/djangoapp')
        else:
            return render(request, 'djangoapp/login.html', context)
    
    else:
        return render(request, 'djangoapp/login.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('/djangoapp')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['password']
        user_exist = False

        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))

        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

# The `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = f"{WEB_ACTION_URL}/dealerships/get-dealership.json"
        # Get dealers from the URL
        context["dealerships"] = restapis.get_dealers_from_cf(url)
        # Concat all dealer's short name
        return render(request, 'djangoapp/index.html', context)

# The `get_dealerships_details` view to render the index page with a list of dealerships
def get_dealership_details(request, state):
    context = {}
    if request.method == "GET":
        url = f"{WEB_ACTION_URL}/dealerships/get-dealership.json"
        # Get dealers from the URL
        context["dealerships"] = restapis.get_dealers_by_state_from_cf(url, state)
        
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = f"{WEB_ACTION_URL}/reviews/get-review.json"
        # Get dealers from the URL
        context["reviews"] = restapis.get_dealer_reviews_by_id_from_cf(url, dealer_id)

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET": 
        url = f"{WEB_ACTION_URL}/dealerships/get-dealership.json?dealerId={dealer_id}"
        # Get dealers from the URL
        context = {
            "cars": CarModel.objects.all(),
            "dealer": restapis.get_dealers_from_cf(url)[0],
        }
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        if request.user.is_authenticated:
            form = request.POST
            review = {
                "name": f"{request.user.first_name} {request.user.last_name}",
                "dealership": dealer_id,
                "review": form["content"],
                "purchase": False
            }
            if form.get("purchase_check"):
                review["purchase"]: True
                review["purchase_date"] = datetime.strftime(datetime.strptime(form.get("purchase_date"), "%m/%d/%Y"), "%m/%d/%Y")
                car = CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.car_make.name
                review["car_model"] = car.name
                review["car_year"]= car.year.strftime("%Y")
            
            json_payload = {"review": review}
            url = f"{WEB_ACTION_URL}/reviews/post-review.json"
            restapis.post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login")
                 