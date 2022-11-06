from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	#first_name, last_name, username, email, number
	user_id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length = 30)
	last_name = models.CharField(max_length = 30)
	password = models.CharField(max_length=64)
	contact_no = models.CharField(max_length=15)
	email = models.CharField(max_length=50)
	is_vendor = models.BooleanField(default = False)

	# For customer
	cart_items = models.JSONField(null = True)
	# { "cart_order_no" : `order_no created for the whole cart`,
	# "list_of_items": [`ids of all the items present in the cart`],
	# }
	wish_list = models.JSONField(null = True)
	# {"list_of_items": [`ids of all the items present in the wishlist`]}
	details = models.JSONField(null = True) 

	# For vendor
	products = models.JSONField(null = True)
	GSTIN = models.CharField(max_length = 50, null = True)

class products(models.Model):
	product_id = models.AutoField(primary_key = True)
	name = models.CharField(max_length=300)
	base_img = models.CharField(max_length=50)
	price = models.FloatField(null=True)
	stock = models.IntegerField(default = 0)
	category = models.CharField(max_length=100, null = True,choices = [("MO","Mobiles"),("CO","Computers"),("CA","Computer accessories"),("TV","TV"),("AP","Appliances"),("EL","Electronics"),("FA","Fashion"),("HO","Home"),("KI","Kitchen"),("PE","Pets"),("BE","Beauty"),("GR","Grocery"),("SP","Sports"),("FI","Fitness"),("BL","Bags and Luggage"),("TB","Toys and Baby products"),("AU","Automobile"),("IN","Industrial"),("BK","Books"),("MO","Movies"),	("MU","Music"),("VG","Video Games"),])
	description = models.CharField(max_length = 2000)
	vendor = models.CharField(max_length = 150)
	weight = models.FloatField()
	height = models.FloatField()
	width = models.FloatField()
	length = models.FloatField()
	guarantee = models.IntegerField()
	colors = models.CharField(max_length=300, null = True)
	reviews = models.JSONField()
	#{ "reviews" : [{"rating" : rating(int), "review" : review(string), "user" : user }, ...] }
	rating = models.FloatField(default = 0)
	no_of_ratings = models.BigIntegerField(default = 0)
	extra_details = models.JSONField()



