from django.contrib import admin
from .models import Product, Cart, Order, Review, User

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Review)