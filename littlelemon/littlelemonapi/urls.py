from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewRetrieve.as_view()),
    path('menu-items/update/<int:pk>', views.SingleMenuItemViewUpdate.as_view()),
    path('menu-items/delete/<int:pk>', views.SingleMenuItemViewDestroy.as_view()),
    path('groups/manager/users',views.managers),
    path('groups/delivery-crew/users',views.delivery_crew),
    path('groups/delivery-crew/users/<int:pk>',views.delivery_crew),
    path('cart/menu-items/',views.CartMenuItemList.as_view()),
    path('cart/menu-items/',views.cart_management),
    path('orders/',views.orders),
    path('orders/<int:pk>',views.order)
]