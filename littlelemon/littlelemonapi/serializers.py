from rest_framework import serializers
from .models import Cart, MenuItem
from django.contrib.auth.models import User
import bleach
#class BookSerializer(serializers.ModelSerializer):
#    class Meta:
 #       model = Book
#        fields = ['id','title','author','price']

class MenuItemSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        return bleach.clean(value)

    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        return super().validate(attrs)
    class Meta():
        model = MenuItem
        fields = ['id','title','price','featured','category']
        extra_kwargs = {
            "price":{"min_value":2}, 
        }

class CartItemSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        return bleach.clean(value)

    def validate(self, attrs):
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        return super().validate(attrs)
    user = serializers.StringRelatedField()
    class Meta():
        model = Cart
        fields = "__all__"
        extra_kwargs = {
            "price":{"min_value":2}, 
        }

class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id','username','email','first_name','last_name']