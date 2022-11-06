from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_func, name="login_func"),
    path("register/", views.register, name="register"),
    path("vendor_register/",views.vendor_register, name="vendor_register"),
    path("logout/",views.logout_func, name="logout_func"),

    path("add_product/", views.add_product, name="add_product"),
    path("product/<int:product_id>/", views.product_view, name="product_view"),
    path("sales_report/", views.sales_report, name="sales_report"),
    path("activate/", views.activate, name="activate"),
    path("add_to_cart/<int:pid>", views.add_to_cart, name = "add_to_cart"),
    path("cart/", views.cart, name = "cart"),
    path("category/<str:category>", views.category, name = "category"),

]