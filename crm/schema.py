import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def validate_phone(phone):
        if not phone:
            return True
        # Accepts +1234567890 or 123-456-7890
        pattern = r'^(\+\d{10,15}|(\d{3}-\d{3}-\d{4}))$'
        return re.match(pattern, phone)

    def mutate(self, info, name, email, phone=None):
        # Check for unique email
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(
                customer=None,
                success=False,
                message="Email already exists."
            )
        # Validate phone format
        if phone and not CreateCustomer.validate_phone(phone):
            return CreateCustomer(
                customer=None,
                success=False,
                message="Invalid phone format. Use +1234567890 or 123-456-7890."
            )
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(
            customer=customer,
            success=True,
            message="Customer created successfully."
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()