from django.urls import path
from . import views

urlpatterns = [
     path('books/', views.BookView.as_view()),
     path('books/<int:pk>', views.SingleBookView.as_view()),
     path('welcome',views.welcome),
     path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),

]