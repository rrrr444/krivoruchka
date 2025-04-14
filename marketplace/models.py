from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="marketplace_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="marketplace_user_permissions",
        blank=True,
    )


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (PENDING, 'В обработке'),
        (SHIPPED, 'Отправлено'),
        (DELIVERED, 'Доставлено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderItem')  # Изменили items на products
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)

    def get_status_class(self):
        return {
            'pending': 'bg-info',
            'shipped': 'bg-warning',
            'delivered': 'bg-success'
        }.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"Заказ #{self.id} - {self.get_status_display()}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.seller_id:
            self.seller = self.product.seller
        super().save(*args, **kwargs)




class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)