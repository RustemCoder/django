from rest_framework import serializers
from .models import Book ,MenuItem
import bleach
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id','title','author','price']

class MenuItemSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        return bleach.clean(value)

    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        if(attrs['inventory']<0):
            raise serializers.ValidationError('Stock cannot be negative')
        return super().validate(attrs)
    class Meta():
        model = MenuItem
        fields = ['id','title','price','inventory']
        extra_kwargs = {
            "price":{"min_value":2}, 
            "inventory":{"min_value":0}
        }