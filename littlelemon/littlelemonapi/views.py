from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem, Cart, Order
from .serializers import  MenuItemSerializer,CartItemSerializer,UserSerializer
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer,StaticHTMLRenderer
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from .custompermissions import IsCustomer, IsDeliveryCrew
from rest_framework import status
# Create your views here.
#@csrf_exempt
#def books(request):
  #  if request.method == 'GET':
 #       books = Book.objects.all().values()
 #       return JsonResponse({"books":list(books)})
#    elif request.method == 'POST':
 #       title = request.POST.get('title')
 #       author = request.POST.get('author')
#        price = request.POST.get('price')
 #       book = Book(
 #           title = title,
 ##          price = price
  #      )
 #       try:
 #           book.save()
 #       except IntegrityError:
  #          return JsonResponse({'error':'true','message':'required field missing'},status=400)

#      return JsonResponse(model_to_dict(book), status=201)

#@api_view
#def book(request):
  #  return Response('list of books',status = status.HTTP_200_OK)

#class BookView(generics.ListCreateAPIView):
    #queryset = Book.objects.all()
  ##  serializer_class = BookSerializer

#class SingleBookView(generics.RetrieveUpdateAPIView):
   # queryset = Book.objects.all()
  #  serializer_class = BookSerializer

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
def welcome(request):
    data = '<html><body><h1>Welcome To Little Lemon API Project</h1></body></html>'
    return Response(data)

@permission_classes([IsAdminUser])
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@permission_classes([IsAdminUser])
class SingleMenuItemViewUpdate(generics.UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@permission_classes([IsAdminUser])
class SingleMenuItemViewDestroy(generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@permission_classes([IsCustomer,IsAdminUser,IsDeliveryCrew])
class SingleMenuItemViewRetrieve(generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@permission_classes([IsAdminUser | IsCustomer])
class CartMenuItemList(generics.ListAPIView):
    serializer_class =  CartItemSerializer
    def get_queryset(self):
        """
        This view should return a list of all the cart menu items
        for the currently authenticated user.
        """
        user = self.request.user
        return Cart.objects.filter(user=user)

@permission_classes([IsAdminUser | IsCustomer])
class CartMenuItemPost(generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class =  CartItemSerializer   



@api_view(['GET'])
def menu_items(request):
    items = MenuItem.objects.all()
    serialized_item = MenuItemSerializer(items,many=True)
    return Response(serialized_item.data)

@api_view(['POST','PATCH','DELETE'])
@permission_classes([IsAdminUser])
def menu_items(request):
     if(request.method =="POST"):
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        category_name = request.query_params.get('search')
        to_price = request.query_params.get('to_price')
        if category_name:
            items =  items.filter(category__title = category_name)
        elif to_price:
            items = items.filter(price_lte=to_price)
        
        if search:
            items = items.filter(title__startswith = search)
            serialized_item = MenuItemSerializer(items, many = True)

@api_view(['POST','DELETE','GET'])
@permission_classes([IsAdminUser])
def managers(request): 
    if(request=="POST" or request=="DELETE"):
        username = request.data['userid']
        if username:
            user = get_object_or_404(User, username = username)
            managers = Group.objects.get(name="Manager")
            if request.method == "POST":
                managers.user_set.add(user)
            elif request.method == "DELETE":
                managers.user_set.remove(user)
        
        return Response({"message":"ok"})
    else:
        managers = User.objects.filter(groups__name="Manager")
        serialized_users = UserSerializer(managers,many = True)
        return Response({"users":serialized_users.data})

@api_view(['POST','DELETE','GET'])
@permission_classes([IsAdminUser])
def delivery_crew(request):
    if(request.method == "GET"):
        delivery_crew = User.objects.filter(groups__name="Delivery Crew")
        serialized_users = UserSerializer(delivery_crew,many = True)
        return Response({"users":serialized_users.data})

    elif(request.method == "POST"):
        username = request.data['username']
        user = get_object_or_404(User, username = username)
        delivery_crew = Group.objects.get(name="Delivery Crew")
        delivery_crew.user_set.add(user)
        return Response("Succesfully created",status = status.HTTP_201_CREATED)
    elif(request.method == "DELETE"):
        username = request.data['username']
        user = get_object_or_404(User, username = username)
        delivery_crew = Group.objects.get(name="Delivery Crew")
        delivery_crew.user_set.remove(user)
        return Response("Succesfully removed",status = status.HTTP_200_OK)


@api_view(['POST','GET','DELETE'])
@permission_classes([IsCustomer])
def cart_management(request):
    if request.method == "GET":
        my_menu_items = Cart.objects.filter(user = request.user)
        serialized_menuitems = MenuItemSerializer(my_menu_items,many = True)
        return Response("My items",{serialized_menuitems.data})

