from django.urls import path
from . import views

#URL config
urlpatterns = [
    path('hello/', views.say_hello),
    path('test_view_2', views.test_view_2),
    path('atatch_files_to_emails', views.atatch_files_to_emails),
    path('use_templated_emails', views.use_templated_emails),
    path('send_email_to_all_customers', views.send_email_to_all_customers)
]