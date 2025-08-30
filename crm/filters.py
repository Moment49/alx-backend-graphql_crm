from .models import Product, Customer, Order
import django_filters


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = django_filters.CharFilter(method='phone_pattern')
   

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'created_at']
    
    def phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)
    
class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price = django_filters.NumberFilter(field_name='price', lookup_expr='incontains')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    stock = django_filters.NumberFilter(field_name='stock', lookup_expr='exact')
    stock__gt = django_filters.NumberFilter(field_name='stock', lookup_expr='gt')
    stock__lt = django_filters.NumberFilter(field_name='stock', lookup_expr='lt')
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

class OrderFilter(django_filters.FilterSet):
    customer__name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gt')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lt')
    total_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='exact')
    product_name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    order_date = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='date')

    class Meta:
        model = Order
        fields = ['customer', "products", "order_date", "total_amount"]

    
