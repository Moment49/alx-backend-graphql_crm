import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products")


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True) 
        email = graphene.String(required=True) 
        phone = graphene.String(required=False) 

    customer = graphene.Field(CustomerType)
   
    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        # Basic email validation
        # Check if email does not exist and unique
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")
        email_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in|edu|net)"
        phone_pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
        if re.search(email_pattern, email):
            print("valid email address  proceed with phone check")
            if phone and re.search(phone_pattern, phone):
                print("proceed with creating the data")
                customer = Customer.objects.create(name=name, email=email, phone=phone)
                customer.save()
            else:
                print("Proceed to create without the phone")
                customer = Customer.objects.create(name=name, email=email)
                customer.save()
        else:
            raise Exception("Invalid email address")
        return CreateCustomer(customer=customer)



class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()




