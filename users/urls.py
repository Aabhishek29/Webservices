from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    # Authentication endpoints
    path('apis/auth/send-otp/', views.send_otp, name='send-otp'),
    path('apis/auth/send-otp-mobile/', views.send_otp, name='send-otp-mobile'),
    path('apis/auth/verify-otp/', views.verify_otp, name='verify-otp'),
    path('apis/auth/signup/', views.signup, name='signup'),
    path('apis/auth/login/', views.login, name='login'),
    path('apis/auth/update-profile/', views.update_user_by_userId, name='update-profile'),
    # Address endpoints
    path('apis/address/add/', views.add_address, name='add-address'),
    path('api/addresses', views.create_address, name='create-address'),
    path('api/addresses/customer/<uuid:customer_id>', views.get_customer_addresses, name='get-customer-addresses'),
    # Other endpoints
    path('apis/subscribe', views.create_subscriber, name='subscribe'),
    path('apis/contact_us_for_project', views.contact_us_for_project, name='contact_us_for_project')
]