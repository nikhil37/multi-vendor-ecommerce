from django.shortcuts import render, redirect
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import *

import os,razorpay,requests,hashlib,json
from string import printable
from random import randint
from bs4 import BeautifulSoup


categories={'Movies': 'MO', 'Computers': 'CO', 'Computer accessories': 'CA', 'TV': 'TV', 'Appliances': 'AP', 'Electronics': 'EL', 'Fashion': 'FA', 'Home': 'HO', 'Kitchen': 'KI', 'Pets': 'PE', 'Beauty': 'BE', 'Grocery': 'GR', 'Sports': 'SP', 'Fitness': 'FI', 'Bags and Luggage': 'BL', 'Toys and Baby products': 'TB', 'Automobile': 'AU', 'Industrial': 'IN', 'Books': 'BK', 'Music': 'MU', 'Video Games': 'VG'}
categories_reverse = {'MO': 'Movies', 'CO': 'Computers', 'CA': 'Computer accessories', 'TV': 'TV', 'AP': 'Appliances', 'EL': 'Electronics', 'FA': 'Fashion', 'HO': 'Home', 'KI': 'Kitchen', 'PE': 'Pets', 'BE': 'Beauty', 'GR': 'Grocery', 'SP': 'Sports', 'FI': 'Fitness', 'BL': 'Bags and Luggage', 'TB': 'Toys and Baby products', 'AU': 'Automobile', 'IN': 'Industrial', 'BK': 'Books', 'MU': 'Music', 'VG': 'Video Games'}

rp_client = razorpay.Client(auth = (settings.RAZOR_API_KEY,settings.RAZOR_API_SECRET))

# { email_hash_md5 :{"user": {first_name = first_name, last_name = last_name, email = email, contact_no = contact_no, password = hash_pass, is_vendor = False, cart_items = {}, wishlist = {}, products = None, GSTIN = None}, "verification_hash": verification_hash()}, }
unverified_profiles = {}

def verification_hash():
	l = ""
	for i in range(20):
		l += printable[randint(0,63)]
	return hashlib.md5(l.encode()).hexdigest()

def password_validate(password):
	if len(password) > 7 and len(password) < 17 and any([char.isdigit() for char in password]) and any([char.isalpha() for char in password]):
		return True
	else:
		return False

def send_email(u,h, email):
	print("sending now")
	to_email = email
	message = render_to_string('confirm_template.html', { "u" : u, "h": h  })
	subject = "Confirm Email and Activate account"
	from_email = settings.EMAIL_HOST_USER
	send_mail(subject = subject, message =  message, from_email =  from_email,
		recipient_list =  [to_email], fail_silently = False, )

def make_order(user, product = None, amount = None):
	if amount != None:
		data = {
			"amount": amount*100,
			"currency" : settings.CURRENCY,
			"receipt" : verification_hash(),
			"notes" : {
				"product_name" : "cart",
				"bought_by" : user.username,
			}
		}
	elif product != None:
		data = {
			"amount": product.price*100,
			"currency" : settings.CURRENCY,
			"receipt" : verification_hash(),
			"notes" : {
				"product_name" : product.name,
				"product_id" : product.product_id,
				"bought_by" : user.username,
				"vendor" : product.vendor
			}
		}
	else:
		return False
	order = rp_client.order.create(data	= data)
	return order

def verify_gstin(gstin):
    req = requests.session()
    req_g = req.get("https://www.mastersindia.co/gst-number-search-and-gstin-verification/")
    csrf = BeautifulSoup(req_g.text, 'html.parser').findAll('input', type="hidden")[0].attrs["value"]
    data = {"postTokenId":csrf, "keyword":gstin}
    req_p = req.post("https://www.mastersindia.co/gst-number-search-and-gstin-verification/", cookies = req_g.cookies, data = data)
    if (len(req_p.text)) == 88478:
        return False
    return True


def index(request):
	if request.GET.get('q') != None:
		query = request.GET.get('q')
		products_n = products.objects.filter(name__contains = query)
		products_d = products.objects.filter(description__contains = query)
		return render(request, "index.html",{"products_n": products_n, "products_d" : products_d, "index":True})
	else:
		products_n = products.objects.all()[:20]
		return render(request, "index.html", {"products_n" : products_n, "index":True})

def category(request, category):
	products_n = products.objects.filter(category = category)
	return render(request, "index.html",{"products_n": products_n, "category":categories_reverse[category]})



def login_func(request):
	if request.method == "POST":
		p = hashlib.sha256(request.POST.get('password').encode()).hexdigest()
		u = request.POST.get('email').split('@')[0]
		u_ = authenticate( username = u, password = p)
		if u_ is None:
			return render(request, "login.html", { "invalid" : True })
		else:
			login(request, u_)
			return redirect(index)
	return render(request, "login.html")

def register(request):
	if request.method == "POST":
		first_name = (request.POST.get('first_name'))
		last_name = (request.POST.get('last_name'))
		email = (request.POST.get('email'))
		contact_no = (request.POST.get('contact_no'))
		password = (request.POST.get('password'))
		confirm = (request.POST.get('confirm'))
		if confirm != password:
			return render(request, "register.html", {"not_match":True})
		if password_validate(password) == False:
			return render(request, "register.html", {"not_valid":True})
		hash_pass = hashlib.sha256(password.encode()).hexdigest()
		h = verification_hash()
		x = {"user" : {"first_name" : first_name, "last_name" : last_name, "email" : email,			"contact_no" : contact_no, "password" : hash_pass, "is_vendor" : False, "cart_items" : [], "wishlist" : [], "products" : [], "GSTIN" : "None"}, "verification_hash": h}
		u = hashlib.md5(email.encode()).hexdigest()
		unverified_profiles[u] = x
		send_email(u,h,email)
		unverified_profiles[hashlib.md5(email.encode()).hexdigest()] = x
		render(request, "index.html")

	return render(request, "register.html")

def vendor_register(request):
	if request.method == "POST":
		first_name = (request.POST.get('first_name'))
		last_name = (request.POST.get('last_name'))
		email = (request.POST.get('email'))
		contact_no = (request.POST.get('contact_no'))
		password = (request.POST.get('password'))
		confirm = (request.POST.get('confirm'))
		gstin = (request.POST.get('GSTIN'))
		if confirm != password:
			return render(request, "register.html", {"not_match":True})
		if password_validate(password) == False:
			return render(request, "register.html", {"not_valid":True})
		hash_pass = hashlib.sha256(password.encode()).hexdigest()
		h = verification_hash()
		x = {"user" : {"first_name" : first_name, "last_name" : last_name, "email" : email,			"contact_no" : contact_no, "password" : hash_pass, "is_vendor" : True, "cart_items" : [], "wishlist" : [], "products" : {"products":[]}, "GSTIN" : gstin}, "verification_hash": h}
		u = hashlib.md5(email.encode()).hexdigest()
		if verify_gstin(gstin) != True:
			return render(request, "vendor_register.html", {"invalid_gstin"})
		unverified_profiles[u] = x
		send_email(u,h,email)
		return redirect(index,)
	return render(request, "vendor_register.html")

def activate(request):
	u = (request.GET.get('u'))
	h = (request.GET.get('h'))
	if u is None or h is None:
		return HttpResponse('Invalid URL.')
	else:
		if unverified_profiles[u]['verification_hash'] == h:
			l = unverified_profiles.pop(u)
			x = User.objects.create_user(first_name = l["user"]["first_name"], last_name = l["user"]["last_name"], username = l["user"]["email"].split('@')[0] , email = l["user"]["email"], contact_no = l["user"]["contact_no"], password = l["user"]["password"], is_vendor = l["user"]["is_vendor"], cart_items = l["user"]["cart_items"], wish_list = l["user"]["wishlist"], products = l["user"]["products"], GSTIN = l["user"]["GSTIN"])
			x.save()
			ul = authenticate(username = l["user"]["email"].split('@')[0],password = l["user"]["password"])
			if ul != None:
				login(request, ul)
				return redirect(index, )
			return redirect(login, )
		else:
			return HttpResponse('Invalid URL.')

def logout_func(request):
	logout(request)
	return redirect(index, )

@login_required(login_url = '/login/')
def add_product(request):
	if request.user.is_vendor == False:
		return redirect(index)
	if request.method == "POST":
		pr_id = str(products.objects.all().count()+1)
		product_name = request.POST.get('product_name')
		description = request.POST.get('description')
		images = request.FILES.getlist('images')
		fs = FileSystemStorage()
		for i,image in enumerate(images):
			if i == 0:
				base_img = 'gotit/static/images/'+pr_id+'_'+str(i)+'.'+image.name.split('.')[-1]
			filename = fs.save('gotit/static/images/'+pr_id+'_'+str(i)+'.'+image.name.split('.')[-1],image)
		category = categories[request.POST.get('category')]
		weight = request.POST.get('weight')
		price = request.POST.get('price')
		length = request.POST.get('length')
		width = request.POST.get('width')
		height = request.POST.get('height')
		stock = request.POST.get('stock')
		guarantee = request.POST.get('guarantee') or 0
		warranty = request.POST.get('warranty') or 0
		color = request.POST.get('color')
		no_of_details = request.POST.get('no_of_details')
		details = {}
		for i in range(1,1+int(no_of_details)):
			if details.get(request.POST.get('detail_title_'+str(i)) ) == None:
				details[request.POST.get('detail_title_'+str(i))] = request.POST.get('detail_'+str(i))
			else:
				return render(request, "add_product.html", {"multiple_detail": True})
		x=products.objects.create(name = product_name, description = description, base_img = base_img, price = price,category = category, vendor = request.user.username, weight = weight, height = height, width = width, length = length, guarantee = guarantee, colors = color , extra_details = details, reviews = { "reviews" : [] })
		x.save()
		redirect(add_product)

	return render(request, "add_product.html")

@login_required
def sales_report(request):
	if request.user.is_vendor == False:
		return redirect(index)
	return render(request, "sales_report.html")

def product_view(request,product_id):
	product = products.objects.filter(product_id= product_id).first()
	reviewed = False
	r = json.loads(product.reviews)["reviews"]
	for i in r:
		if request.user.username == i["user"]:
			reviewed = True
			return render(request, "product_view.html", {"product":product , "images" : imgs, "main_image": imgs[0]["src"], "order_id" : order_id, "reviewed" : reviewed})
	if request.method == "POST":
		r.append({"rating": request.POST.get('rating'), "review": request.POST.get('review'), "user": request.user.username})
	x = os.listdir('gotit/static/images/')
	imgs = []
	for j,i in enumerate(x):
		if i.startswith(str(product_id)):
			imgs.append({"src":"/static/images/"+i,"num":j})
	order_id = make_order(user = request.user, product = product)["id"]
	return render(request, "product_view.html", {"product":product , "images" : imgs, "main_image": imgs[0]["src"], "order_id" : order_id, "reviewed" : reviewed})

@csrf_exempt
def add_to_cart(request, pid):
	u = request.user
	cart = u.cart_items
	if cart == None:
		cart = [pid]
	else:
		try:
			cart.append(pid)
		except KeyError:
			cart = [pid]
	u.cart_items = cart
	u.save()
	return JsonResponse({"added" : True})

def cart(request):
	pids = request.user.cart_items
	if request.method == "POST":
		p = int(request.POST.get('pid'))
		try:
			print(p,pids)
			pids.remove(p)
		except ValueError:
			pass
		u = request.user
		u.cart_items = pids
		u.save()
	products_cart = []
	amt = 0
	for pid in pids:
		l = products.objects.filter(product_id = pid).first()
		amt += l.price
		products_cart.append(l)
	order = make_order(request.user, amount = amt)
	return render(request, "checkout.html", {"products":products_cart, "order_id":order["id"], "amount": amt})

