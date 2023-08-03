from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem, Cart, Order
from .serializers import  MenuItemSerializer,CartItemSerializer, OrderSerializer,UserSerializer
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer,StaticHTMLRenderer
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from .custompermissions import IsCustomer, IsDeliveryCrew
from rest_framework import status
import datetime
# Create your views here.

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['category__title']
    ordering_fields = ['price', 'inventory']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

@permission_classes([IsAdminUser])
class MenuItemsViewOld(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

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

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("ok")

class CartMenuItemPost(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class =  CartItemSerializer
    permission_classes = [IsCustomer,IsAdminUser]



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
    elif(request.method == "POST"):
        menu_item = MenuItem.objects.get(id=request.data["menu_item"])
        price = menu_item.price * int(request.data["quantity"])

        if Cart.objects.filter(user=request.user).exists():
            cart = Cart.objects.get(user=request.user)
        else:
            cart = Cart.objects.create(user=request.user, quantity=request.data["quantity"], menuitem=menu_item, unit_price=menu_item.price, price=price)
        
        serialized = CartItemSerializer(cart)
        return Response(serialized.data, status=HTTP_201_CREATED)
    elif(request.method == "DELETE"):
        cart = Cart.objects.filter(user = request.user)
        cart.delete()
        serialized = CartItemSerializer(cart)
        return Response(serialized.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET","POST"])
@permission_classes([IsCustomer])
def customer_orders(request):
    if(request.method == "GET"):
        orders = Order.objects.filter(user = request.user)
        serialized = OrderSerializer(orders,many = True)
        return Response(serialized.data,status=status.HTTP_200_OK)
    elif(request.method == "POST"):
        cart = Cart.objects.filter(user = request.user)
        total = 0
        quantity = 0
        for item in cart:
            order = Order.objects.create(user = request.user,quantity = item["quantity"],status = 1 ,total = item["quantity"]*item["price"], date = datetime.datetime.now(),delivery_crew=item["menuitem"])
        
        
        cart.delete()
        serialized = OrderSerializer(order,many = True)
        return Response(serialized.data, status=status.HTTP_200_OK)


class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.count()==0: #normal customer - no group
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Delivery Crew').exists(): #delivery crew
            return Order.objects.all().filter(delivery_crew=self.request.user)  #only show oreders assigned to him
        else: #delivery crew or manager
            return Order.objects.all()
        # else:
        #     return Order.objects.all()

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message:": "no item in cart"})

        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if (order_serializer.is_valid()):
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=self.request.user).all()

            for item in items.values():
                orderitem = OrderItem(
                    order=order,
                    menuitem_id=item['menuitem_id'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                orderitem.save()

            Cart.objects.all().filter(user=self.request.user).delete() #Delete cart items

            result = order_serializer.data.copy()
            result['total'] = total
            return Response(order_serializer.data)
    
    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total



class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
            return Response('Not Ok')
        else: #everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)


class GroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Manager')
        items = UserSerilializer(users, many=True)
        return Response(items.data)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        return Response({"message": "user added to the manager group"}, 200)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": "user removed from the manager group"}, 200)

class DeliveryCrewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        users = User.objects.all().filter(groups__name='Delivery Crew')
        items = UserSerilializer(users, many=True)
        return Response(items.data)

    def create(self, request):
        #only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.add(user)
        return Response({"message": "user added to the delivery crew group"}, 200)

    def destroy(self, request):
        #only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.remove(user)
        return Response({"message": "user removed from the delivery crew group"}, 200)   

