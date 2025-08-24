from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('apis/auth/send-otp/', views.send_otp, name='send-otp'),
    path('apis/auth/verify-otp/', views.verify_otp, name='verify-otp'),
    path('apis/auth/update-profile/', views.update_user_by_userId, name='update-profile'),
    path('apis/address/add/', views.add_address, name='add-address'),
    path('apis/subscribe', views.create_subscriber, name='subscribe'),
    path('apis/contact_us_for_project', views.contact_us_for_project, name='contact_us_for_project')
]