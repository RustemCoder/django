from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewRetrieve.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewUpdate.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewDestroy.as_view()),
    path('groups/manager/users',views.managers),
]