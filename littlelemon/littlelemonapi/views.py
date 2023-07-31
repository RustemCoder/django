from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem
from .serializers import  MenuItemSerializer
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer,StaticHTMLRenderer
from rest_framework.decorators import api_view, renderer_classes
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

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@api_view(['GET', 'POST'])
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
    elif (request.method == "GET"):
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializer(items,many=True)
    return Response(serialized_item.data)

