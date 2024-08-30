from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class Customer(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ("user", "User"),
        ("manufacturer", "Manufacturer"),
    ]

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    full_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True, blank=True)
    company_logo_image = models.ImageField(
        upload_to="logo_images/", null=True, blank=True
    )
    country = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    login_status = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username"]

    # def __str__(self):
    #     return str(self.id)

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return None

    @staticmethod
    def get_customer_by_username(username):
        try:
            return Customer.objects.get(username=username)
        except Customer.DoesNotExist:
            return None


class Categoryies(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/")
    description = models.TextField()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product_name = models.CharField(max_length=255)
    manufacturer_id = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="products"
    )
    quantity = models.PositiveIntegerField()
    product_image = models.ImageField(
        upload_to="product_images/", null=True, blank=True
    )
    unit_weight = models.FloatField()
    product_description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_short_description = models.TextField(default=" ")
    categories = models.ManyToManyField(Categoryies, related_name="products")
    tags = models.ManyToManyField(Tag, related_name="products")

    def __str__(self):
        return self.product_name


# Add to Cart Functionality


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="23223")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def update_total(self):
        # Calculate total price and quantity based on CartItems
        total_price = Decimal(0)
        total_quantity = 0

        for item in self.items.all():
            total_price += item.product.unit_price * item.quantity
            total_quantity += item.quantity

        # Update the Cart's total price and quantity
        self.total_price = total_price
        self.total_quantity = total_quantity
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # Update the cart's total price and total quantity when saving a CartItem
        self.cart.total_price += self.product.unit_price * self.quantity
        self.cart.total_quantity += self.quantity
        self.cart.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update the cart's total price and total quantity when deleting a CartItem
        self.cart.total_price -= self.product.unit_price * self.quantity
        self.cart.total_quantity -= self.quantity
        self.cart.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} in {self.cart.user.username}'s Cart"


class Order(models.Model):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (SHIPPED, "Shipped"),
        (DELIVERED, "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.product_name} in Order #{self.order.id}"
        )


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = (
        models.IntegerField()
    )  # You can customize this field based on your rating system
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.reviewer.username}"
