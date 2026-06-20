from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_flights, name='search'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-fleet/', views.admin_fleet, name='admin_fleet'),
    path('admin-bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-users/', views.admin_users, name='admin_users'),
]
