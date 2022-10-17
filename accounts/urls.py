from django.urls import path
from .import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),   #we need pass the uid and the token
    path('dashboard',views.dashboard,name="dashboard"),
    #now I want made adjustment to the URL localhost:8000/accounts only, also directly to the dashboard
    path('',views.dashboard,name="dashboard"),
    # forgot password URL
    path('forgotpassword',views.forgotpassword,name="forgotpassword"),
    path('resetpass/<uidb64>/<token>',views.resetpassword_validate,name="resetpassword_validate"),
    path('resetpass/',views.resetpassword,name="resetpassword"),
]
