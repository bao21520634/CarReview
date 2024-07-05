from django.db import models
from django.utils.timezone import now


# Create models here.
# Car Make
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=300)

    def __str__(self):
        return "Name: " + self.name + "\n" + \
                "Description: " + self.description

class CarModel(models.Model):

    sedan = 'Sedan'
    suv = 'SUV'
    wagon = 'WAGON'
    others = "Others"
    car_choices = [(sedan, 'Sedan'), (suv, 'SUV'), (wagon, 'WAGON'), (others, 'Others')]

    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=30)
    dealer_id = models.IntegerField(null=True)
    car_type = models.CharField(null=False, max_length=30, choices=car_choices)
    year = models.DateField(null=True)

    def __str__(self):
        return "Name: " + self.name + "\n" + \
                "Type: " + self.car_type  


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, state, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer state
        self.state = state
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:

    def __init__(self, name , dealership , review , purchase, purchase_date , car_make , car_model , car_year, sentiment):
        self.name = name
        self.dealership = dealership
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment

    def __str__(self):
        return "Review: " + self.review