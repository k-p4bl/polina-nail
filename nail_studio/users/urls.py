from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    path("all_past_sign_ups/", views.all_past_sign_ups, name="all_past_sign_ups"),
    path("ban_list/", views.ban_list, name="ban_list"),
    path("ban_user/", views.ban_user, name="ban_user"),
    path("unban_list/", views.unban_list, name="unban_list"),
    path("unban_user/", views.unban_user, name="unban_user"),
    path("delete_sign_up/<int:pk>/", views.delete_sign_up, name="delete_sign_up"),
    path('future_sign_ups/', views.future_sign_ups, name="f_sign_ups"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path("future_sign_ups/<int:pk>/", views.future_sign_up, name="future_sign_up"),
    path('flash_call/', views.flash_call, name='flash_call'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('login_not_staff/', views.login_not_staff, name='login_not_staff'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("master_p_sign_ups/", views.master_p_sign_ups, name="master_p_sign_ups"),
    path("move_sign_up/<int:pk>/", views.move_sign_up, name="move_sign_up"),
    path('past_sign_ups/', views.past_sign_ups, name="p_sign_ups"),
    path('personal-account/', views.personal_account, name="personal-account"),
    path('phone-check/', views.phone_check, name="phone_check"),
    path('register/', views.register, name='register'),
    path('refactor/', views.refactor_personal_data, name="refactor_personal_data"),
    path('sign_up/<int:pk>/', views.sign_up, name="sign_up"),
    path("week_future_sign_ups/", views.week_future_sign_ups, name="week_future_sign_ups"),
]