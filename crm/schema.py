import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re
from django.db import transaction, IntegrityError
from decimal import Decimal


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
        fields = ("id", "customer", "products")


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

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
        # name = graphene.String(required=True) 
        # email = graphene.String(required=True) 
        # phone = graphene.String(required=False) 

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


# QUERY 

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info, **kwargs):
        return Customer.objects.all()
    
    def resolve_products(root, info, **kwargs):
        return Product.objects.all()
    
    def resolve_orders(root, info, **kwargs):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()




