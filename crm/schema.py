import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re
from django.db import transaction, IntegrityError
from decimal import Decimal
from django.utils import timezone


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock", "price")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")


# Create an input type for the customer data
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

# Input Type for Products data
class ProductsInput(graphene.InputObjectType):
    name = graphene.String()
    stock = graphene.Int()
    price =  graphene.Float()


# Input Type for Orders data
class OrderInput(graphene.InputObjectType):
    product_ids = graphene.List(graphene.ID, required=True)
    customer_id = graphene.ID(required=True)
    order_date = graphene.DateTime(required=False)



class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
   
    @classmethod
    def mutate(cls, root, info, input):
        # Basic email validation
        # Check if email does not exist and unique
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        email_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in|edu|net)"
        phone_pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
        if re.search(email_pattern, input.email):
            print("valid email address  proceed with phone check")
            if input.phone and re.search(phone_pattern, input.phone):
                print("proceed with creating the data")
                customer = Customer.objects.create(name=input.name, email=input.email, phone=input.phone)
                customer.save()
            else:
                print("Proceed to create without the phone")
                customer = Customer.objects.create(name=input.name, email=input.email)
                customer.save()
        else:
            raise Exception("Invalid email address")
        
        return CreateCustomer(customer=customer, message="Customer created successfully")



class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        # Pass a list of the *input type*
        input = graphene.List(CustomerInput)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        customers = []
        errors = []
        # Phone pattern and email pattern
        email_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in|edu|net)"
        phone_pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")

        try:
            with transaction.atomic():  
                for index, data in enumerate(input):
                    # Basic validation
                    if not data.name or not data.email:
                        errors.append(f"Row {index+1}: Name and Email are required.")
                        continue
                    if re.search(email_pattern, data.email) is None:
                        errors.append(f"Row {index+1}: Invalid email: {data.email}")
                        continue

                    if data.phone and re.search(phone_pattern, data.phone) is None:
                        errors.append(f"Row {index+1}: Invalid Phone: {data.phone}")
                        continue
                    # Check for duplicate emails
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"Row {index+1}: Email '{data.email}' already exists.")
                        continue
                    
                    # Create the customer if all the validation passes and the phone number is provided
                    # Fix the conditional logic for checking phone number to ensure its created without phone no provided
                    customer = Customer(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    customer.save()
                    customers.append(customer)

                # If errors happened, rollback (no customers saved)
                if errors:
                    raise IntegrityError("Some records failed, rolling back.")

        except IntegrityError:
            customers = []  # rollback, nothing saved

        return BulkCreateCustomers(
            customers=customers,
            errors=errors
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductsInput(required=True)


    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        price = input.price
        stock = input.stock
        name = input.name 
       
        # Create the product 
        if stock < 0:
            raise Exception("Stock cannot be negative")
        
        if price < 0:
            raise Exception("Price cannot be negative")
        
        # Convert price from default float type to python native decimal before saving
        price = Decimal(str(price))
        
        create_product = Product.objects.create(name=name, stock=stock, price=price)
        create_product.save()
       
        return CreateProduct(product=create_product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
   
    @classmethod
    def mutate(cls, root, info, input):
        total_amount = 0

        # Get the products to see if they exist
        products = Product.objects.filter(pk__in=input.product_ids)

        # Get the customer to see if it exists
        if not Customer.objects.filter(pk=input.customer_id).exists():
            raise Exception("Sorry Invalid customer Id")
        
        # Check if the product IDs are valid
        if not input.product_ids:
            raise Exception("Product IDs list cannot be empty")
        
        if not products.exists() or products.count() != len(input.product_ids):
            raise Exception("No valid products found for the given IDs")
        

        # Caculate the total price from the products
        for product in products:
            total_amount += product.price
        
        # Create the order
        order_date = input.order_date or timezone.now()
        customer = Customer.objects.get(pk=input.customer_id)
        order = Order.objects.create(customer=customer, total_amount=total_amount, order_date=order_date)
        order.save()

        # Associate an order with a product
        order.products.set(products)

        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    success = graphene.String()
    updated_products = graphene.List(ProductType)


    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10  # simulate restock
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            success="Low stock products updated successfully",
            updated_products=updated,
        )



# QUERY 
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_all_customers(root, info, **kwargs):
        return Customer.objects.all()
    
    def resolve_products(root, info, **kwargs):
        return Product.objects.all()
    
    def resolve_orders(root, info, **kwargs):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()




