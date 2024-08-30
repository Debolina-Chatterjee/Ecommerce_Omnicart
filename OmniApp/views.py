# views.py

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.views import View
from .forms import *
from django.db.models import Q, Count
from .models import Customer, Order, Categoryies, Tag
from django.contrib.auth.hashers import check_password
from django.urls import reverse
import re
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from uuid import UUID
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import datetime
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from django.http import HttpResponse
from django.template.defaulttags import register


@register.filter
def get_range(value):
    return range(value)


def authentication_login(request):
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            # Try to fetch the customer if the ID is available
            customer = Customer.objects.get(id=customer_id)
            user_authenticated = True
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist
            user_authenticated = False
            customer = None
    else:
        # Customer session is not available, user is not authenticated
        user_authenticated = False
        customer = None
    types = customer.user_type if customer else None
    return user_authenticated, types


def index(request):
    # Get the customer session from the session
    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/index.html", context)


# def cart_view(request):
#     customer_id = request.session.get("customer")
#     # Check if the customer is authenticated
#     user_authenticated = customer_id is not None

#     context = {
#         "user_authenticated": user_authenticated,
#         "current_page_url": request.path,
#     }
#     return render(request, "OmniCart/cart.html", context)


class CustomLoginView(View):
    template_name = "OmniCart/Authintication/login.html"
    return_url = None

    def get(self, request):
        CustomLoginView.return_url = request.GET.get("return_url")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("username")
        password = request.POST.get("password")

        if re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email):
            customer = Customer.get_customer_by_email(email)
        else:
            customer = Customer.get_customer_by_username(email)

        error_message = None
        user_type = None

        if customer and check_password(password, customer.password):
            # Convert the UUID to a string before storing it in the session
            request.session["customer"] = {
                "id": str(customer.id),
                "username": customer.username,
            }
            user_type = customer.user_type

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                if customer.user_type == "manufacturer":
                    # Redirect to the manufacturer admin panel
                    return redirect(
                        reverse("admin_panel", kwargs={"customer_id": str(customer.id)})
                    )
                else:
                    if CustomLoginView.return_url:
                        return HttpResponseRedirect(CustomLoginView.return_url)
                    else:
                        CustomLoginView.return_url = None
                        # Redirect to the home page or another named URL
                        return redirect("index")
            else:
                error_message = "Authentication failed"
        else:
            error_message = "Invalid login credentials"

        context = {
            "type": user_type,
            "customer": customer,
            "error_message": error_message,
            "user_authenticated": False,
        }

        return render(request, self.template_name, context)


class RegistrationView(View):
    template_name = "OmniCart/Authintication/register.html"

    def get(self, request):
        form = CustomerCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomerCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])  # Use 'password1' here
            user.save()
            User = get_user_model()
            new_user = User.objects.create_user(
                username=user.username,
                email=user.email,
                password=form.cleaned_data["password1"],
            )
            new_user.save()
            return redirect("login")  # Change 'login' to your login URL

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    template_name = "OmniCart/Authintication/logout.html"

    def get(self, request):
        request.session.clear()
        logout(request)
        return redirect("login")

    def post(self, request):
        # You can add addition
        return self.get(request)


class AdminPanelView(View):
    template_name = "OmniCart/admin/admin_panel.html"

    def get(self, request, customer_id):
        try:
            customer = request.user
            customers = Customer.objects.get(id=customer_id, user_type="manufacturer")
            total_products = Product.objects.filter(manufacturer_id=customers).count()
            pending_orders = Order.objects.filter(
                status="pending", user=customer
            ).order_by("-order_date")
            order_count = OrderItem.objects.filter(
                product__manufacturer_id=customers
            ).count()
            # Count orders with each status related to the manufacturer's products
            pending_count = OrderItem.objects.filter(
                product__manufacturer_id=customers, order__status="pending"
            ).count()
            processing_count = OrderItem.objects.filter(
                product__manufacturer_id=customers, order__status="processing"
            ).count()
            shipped_count = OrderItem.objects.filter(
                product__manufacturer_id=customers, order__status="shipped"
            ).count()
            delivered_count = OrderItem.objects.filter(
                product__manufacturer_id=customers, order__status="delivered"
            ).count()
            # Get total sales month-wise
            sales_data = (
                Order.objects.filter(
                    user=customer,
                    status=Order.DELIVERED,
                )
                .annotate(month=TruncMonth("order_date"))
                .values("month")
                .annotate(total_sales=Sum("items__unit_price"))
                .order_by("month")
            )

            # Prepare data for charting
            month_labels = []
            total_sales_data = []
            for sale in sales_data:
                month_labels.append(sale["month"].strftime("%B %Y"))
                total_sales = sale["total_sales"]
                if total_sales is None:
                    total_sales = 0.0  # Set default value if total_sales is None
                total_sales_data.append(float(total_sales))  # Convert to float

            total_sales_data_json = json.dumps(total_sales_data)

            return render(
                request,
                self.template_name,
                {
                    "customer": customer,
                    "total_products": total_products,
                    "total_orders": order_count,
                    "month_labels": month_labels,
                    "pending_orders": pending_orders,
                    "pending_count": pending_count,
                    "processing_count": processing_count,
                    "shipped_count": shipped_count,
                    "delivered_count": delivered_count,
                    "total_sales_data": total_sales_data_json,  # Pass as JSON
                    # "logo": customers.company_logo_image.url,
                },
            )
        except Customer.DoesNotExist:
            return render(
                request,
                "OmniCart/error.html",
                {"error_message": "Invalid customer ID or user type."},
            )


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        customer_session = request.session.get("customer")
        logo = ""
        if customer_session:
            if form.is_valid():
                product = form.save(commit=False)
                customer_id = customer_session.get("id")
                customer = Customer.objects.get(
                    id=customer_id, user_type="manufacturer"
                )
                product.manufacturer_id = customer
                product.save()
                form.save_m2m()  # Save many-to-many fields
                messages.success(request, "Product added successfully!")
                return redirect("add_product")
            else:
                error_message = "There was an error. Please check the form."
        else:
            error_message = "Please log in as a manufacturer."
    else:
        form = ProductForm()
        error_message = None

    return render(
        request,
        "OmniCart/admin/add_product.html",
        {
            "form": form,
            "error_message": error_message,
            # "logo": customer.company_logo_image.url,
        },
    )


# Listing of all the Produts
def product_list(request):
    # Check if the customer is logged in and is a manufacturer
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")
            # Filter products based on the manufacturer ID
            products = Product.objects.filter(manufacturer_id=customer)
            return render(
                request, "OmniCart/admin/product_list.html", {"products": products}
            )
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist or is not a manufacturer
            messages.error(request, "Invalid customer or not a manufacturer.")
            return redirect("login")  # Redirect to the login page or handle as needed
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")  # Redirect to the login page or handle as needed


def product_edit(request, product_id):
    customer_session = request.session.get("customer")
    # Retrieve the product object
    product = get_object_or_404(Product, product_id=product_id)
    if customer_session:
        if request.method == "POST":
            # Populate the form with the submitted data and instance
            form = ProductEditrm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                # Save the updated data
                form.save()
                return redirect(
                    "product_list"
                )  # Redirect to the product list page after successful update
        else:
            # Populate the form with the current product data
            form = ProductEditrm(instance=product)
        return render(
            request,
            "OmniCart/admin/product_edit.html",
            {"form": form, "product": product},
        )
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")


def product_delete(request, product_id):
    customer_session = request.session.get("customer")

    product = get_object_or_404(Product, product_id=product_id)

    # Check if the request method is POST
    if request.method == "POST":
        # Delete the product
        product.delete()

        # Return a JSON response indicating success
        return JsonResponse({"message": "Product deleted successfully."})

    # Return a JSON response indicating an error (this should not happen in a valid scenario)
    return JsonResponse({"error": "Invalid request method."}, status=400)


def shop(request):
    # Assuming you have a queryset for products and categories
    products = Product.objects.all()
    # categories = Category.objects.all()
    customer_id = request.session.get("customer")
    # Check if the customer is authenticated
    user_authenticated = customer_id is not None
    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 9)  # Show 9 products per page
    try:
        product_pages = paginator.page(page)
    except PageNotAnInteger:
        product_pages = paginator.page(1)
    except EmptyPage:
        product_pages = paginator.page(paginator.num_pages)

    context = {
        "products": product_pages,
        # 'categories': categories,
        "user_authenticated": user_authenticated,
        "current_page": int(page),
        "product_pages": range(1, product_pages.paginator.num_pages + 1),
    }

    return render(request, "OmniCart/product/shop.html", context)


# Order View
def order_list(request):
    # Check if the logged-in user is a manufacturer
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")
            # Filter products based on the manufacturer ID
            products = Product.objects.filter(manufacturer_id=customer)
            orders = Order.objects.filter(items__product__in=products).distinct()
            return render(
                request, "OmniCart/admin/order/view-order.html", {"orders": orders}
            )
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist or is not a manufacturer
            messages.error(request, "Invalid customer or not a manufacturer.")
            return redirect("login")  # Redirect to the login page or handle as needed
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")


def order_detail(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)
    # print(order.user_id)
    # Retrieve the customer who placed the order
    customer = get_object_or_404(User, id=order.user_id)
    customers = Customer.objects.get(email=customer.email)

    # You can customize this context based on your requirements
    context = {
        "order": order,
        "customer": customers,
    }

    return render(request, "OmniCart/admin/order/order_detail.html", context)


def update_order_status(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Get the new status from the form
        new_status = request.POST.get("status")
        if new_status:
            # Update the order status
            order.status = new_status
            order.save()
            # Redirect back to the order list page
            return redirect("order_list")

    # If the request method is not POST or status is not provided, redirect back to the order list page
    return redirect("order_list")


def shops(request):
    # Assuming you have a queryset for products and categories
    products = Product.objects.all()
    user_authenticated, types = authentication_login(request)
    # categories = Category.objects.all()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 9)  # Show 9 products per page
    try:
        product_pages = paginator.page(page)
    except PageNotAnInteger:
        product_pages = paginator.page(1)
    except EmptyPage:
        product_pages = paginator.page(paginator.num_pages)

    context = {
        "products": product_pages,
        # 'categories': categories,
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page": int(page),
        "product_pages": range(1, product_pages.paginator.num_pages + 1),
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/shops.html", context)


@login_required(login_url="login")
def product_detail(request, product_id):
    # Retrieve the product details based on the product_id
    product = get_object_or_404(Product, product_id=product_id)
    manufacturer = product.manufacturer_id
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    user_authenticated, types = authentication_login(request)
    from django.template.defaulttags import register

    register.filter("get_range", get_range)

    context = {
        "product": product,
        "cart": cart,
        "item": cart_item,
        "manufacturer": manufacturer,
        "user_authenticated": user_authenticated,
        "type": types,
    }

    return render(request, "OmniCart/product/product_detail.html", context)


@login_required(login_url="login")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    user = request.user

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=user)

    # Check if the product is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    # If the item is already in the cart, increase the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required(login_url="login")
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    user_authenticated, types = authentication_login(request)

    context = {
        "cart": cart,
        "user_authenticated": user_authenticated,
        "type": types,
    }

    return render(request, "OmniCart/cart.html", context)


def update_cart_quantity(request, item_id, new_quantity):
    try:
        # Get the CartItem based on the item_id
        cart_item = CartItem.objects.get(id=item_id)

        # Update the quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        # Update the total price and quantity in the Cart
        cart_item.cart.update_total()

        return JsonResponse({"success": True})
    except CartItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "CartItem does not exist"})


def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()

        return JsonResponse({"success": True})
    except CartItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "CartItem does not exist"})


# Now Checkout page


@login_required(login_url="login")
def checkout(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    user_authenticated, types = authentication_login(request)

    customer_session = request.session.get("customer")
    customer_id = customer_session.get("id") if customer_session else None

    if customer_id:
        customer = Customer.objects.get(id=customer_id)
    else:
        customer = None

    if request.method == "POST":
        try:
            # Create a new order
            order = Order.objects.create(user=user, total_price=cart.total_price)

            # Move cart items to order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.unit_price,
                )

            # Clear the cart
            cart_items = cart.items.all()

            # Delete cart items individually using filter
            for cart_item in cart_items:
                cart_item.delete()

            # Delete the cart
            cart.delete()

            # Redirect to a success page
            return redirect(reverse("order_success", kwargs={"order_id": order.id}))

        except Exception as e:
            print(f"Error during checkout: {e}")

    context = {
        "cart": cart,
        "user_authenticated": user_authenticated,
        "customer": customer,
        "type": types,
    }
    return render(request, "OmniCart/checkout.html", context)


def order_success(request, order_id):
    # Fetch the order and customer information
    try:
        order = Order.objects.get(id=order_id)
        user_authenticated, types = authentication_login(request)
        customer_session = request.session.get("customer")
        customer_id = customer_session.get("id") if customer_session else None

        if customer_id:
            customer = Customer.objects.get(id=customer_id)
        else:
            customer = None

    except Order.DoesNotExist or Customer.DoesNotExist:
        return redirect("index")

    context = {
        "order": order,
        "customer": customer,
        "user_authenticated": user_authenticated,
        "type": types,
    }

    return render(request, "OmniCart/order_success.html", context)


# Get All The Categories


def get_categories(request):
    categories = Categoryies.objects.all().values("id", "name")
    return JsonResponse(list(categories), safe=False)


def category_view(request, category_id):
    # Get category
    category = Categoryies.objects.get(id=category_id)
    # Get products in the category
    products = Product.objects.filter(categories__id=category_id)
    # Paginate products
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get("page")
    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    return render(
        request,
        "OmniCart/product/category.html",
        {"products": products_page, "category": category},
    )


def get_tag(request):
    tags = Tag.objects.all().values("id", "name")
    return JsonResponse(list(tags), safe=False)


def tag_view(request, tag_id):
    # Get tag
    tag = Tag.objects.get(id=tag_id)
    # Get products associated with the tag
    products = Product.objects.filter(tags__id=tag_id)
    # Paginate products
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get("page")
    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)
    return render(
        request, "OmniCart/product/tag.html", {"products": products_page, "tag": tag}
    )


def search_view(request):
    query = request.GET.get("search")

    if query:
        # Search products, categories, and tags
        products = Product.objects.filter(product_name__icontains=query)
        categories = Categoryies.objects.filter(name__icontains=query)
        tags = Tag.objects.filter(name__icontains=query)

        # Get products associated with matching categories and tags
        category_products = Product.objects.filter(categories__name__icontains=query)
        tag_products = Product.objects.filter(tags__name__icontains=query)

        # Merge product lists to remove duplicates
        associated_products = (category_products | tag_products).distinct()
    else:
        products = categories = tags = associated_products = None

    context = {
        "query": query,
        "products": products,
        "categories": categories,
        "tags": tags,
        "associated_products": associated_products,
    }
    return render(request, "OmniCart/product/search_results.html", context)


@login_required(login_url="login")
def my_account(request):
    user_authenticated, types = authentication_login(request)
    customer = get_object_or_404(User, id=request.user.id)
    customers = Customer.objects.get(email=customer.email)

    # Filter orders based on status (assuming pending status is "pending")
    pending_orders = Order.objects.filter(user=request.user, status="pending")

    context = {
        "user_authenticated": user_authenticated,
        "customer": customers,
        "pending_orders": pending_orders,
    }
    return render(request, "OmniCart/Authintication/my-account.html", context)


def shipping(request):

    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request, "OmniCart/info/shipping.html", context)


def privacy(request):

    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request, "OmniCart/info/privacy.html", context)


def pymntmethods(request):

    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request, "OmniCart/info/pymntmethods.html", context)


def returns(request):

    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request, "OmniCart/info/returns.html", context)


def moneyback(request):

    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request, "OmniCart/info/moneyback.html", context)


def about_us(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/info/aboutus.html", context)


def contact_us(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/info/contactus.html", context)


def faq(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/info/faq.html", context)


def help(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/info/help.html", context)


def terms_and_condition(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/info/termsandcondition.html", context)


@login_required(login_url="login")
def update_customer_info(request):
    if request.method == "POST":
        customer_id = request.POST.get(
            "customer_id"
        )  # Assuming you have a hidden input field in your form containing the customer ID
        customer = Customer.objects.get(id=customer_id)  # Get the Customer instance
        # Update the customer fields with the form data
        customer.full_name = request.POST.get("full_name")
        customer.address = request.POST.get("address")
        customer.country = request.POST.get("country")
        customer.postal_code = request.POST.get("postal_code")
        customer.phone_number = request.POST.get("phone_number")
        customer.company = request.POST.get("company")
        # Save the updated customer instance
        customer.save()
        return redirect(
            "my_account"
        )  # Redirect to the profile page after saving changes
    else:
        return redirect("my_account")


@login_required(login_url="login")
def admin_account(request):
    user_authenticated, types = authentication_login(request)
    customer = get_object_or_404(User, id=request.user.id)
    customers = Customer.objects.get(email=customer.email)
    pending_orders = Order.objects.filter(user=request.user, status="pending")

    # Filter orders based on status (assuming pending status is "pending")

    context = {
        "user_authenticated": user_authenticated,
        "customer": customers,
        "pending_orders": pending_orders,
    }
    return render(request, "OmniCart/admin/admin-account.html", context)


def update_admin_customer_info(request):
    if request.method == "POST":
        # Retrieve form data
        full_name = request.POST.get("full_name")
        address = request.POST.get("address")
        country = request.POST.get("country")
        postal_code = request.POST.get("postal_code")
        phone_number = request.POST.get("phone_number")
        company = request.POST.get("company")

        # Get the uploaded company logo file
        company_logo = request.FILES.get("company_logo")

        # Retrieve the admin customer object using the customer_id
        customer_id = request.POST.get("customer_id")
        admin_customer = Customer.objects.get(id=customer_id)

        # Update the admin customer object with the new data
        admin_customer.full_name = full_name
        admin_customer.address = address
        admin_customer.country = country
        admin_customer.postal_code = postal_code
        admin_customer.phone_number = phone_number
        admin_customer.company = company

        # Check if a new company logo was uploaded
        if company_logo:
            admin_customer.company_logo_image = company_logo

        # Save the changes
        admin_customer.save()

        # Redirect to the appropriate page
        return redirect(
            "admin_account"
        )  # Change 'profile' to the name of your profile page URL pattern
    else:
        return redirect("index")


@login_required
def add_review(request, product_id):
    if request.method == "POST":
        product = Product.objects.get(pk=product_id)
        reviewer = request.user
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            # Create the review
            Review.objects.create(
                product=product, reviewer=reviewer, rating=rating, comment=comment
            )
            messages.success(request, "Your review has been submitted successfully.")
        else:
            messages.error(
                request, "Please provide both rating and comment for the review."
            )

    return redirect("product_detail", product_id=product_id)
