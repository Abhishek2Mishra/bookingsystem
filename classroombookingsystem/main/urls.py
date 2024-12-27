from django.urls import path
from main.views import (BookSeatView, UpdateClassroomView, CreateClassroomView, DashboardView, UserLoginView,UserRegisterView,AvailableClassroomsView)
app_name = 'main'  # Define the app namespace


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='api_register'),
    path('login/', UserLoginView.as_view(), name='api_login'),
    # path('user-detail/', UserDetailView.as_view(), name='api_user_detail'),
    path('dashboard/', DashboardView.as_view(), name='api_dashboard'),
    path('classrooms/create/', CreateClassroomView.as_view(), name='api_create_classroom'),
    path('classrooms/<int:pk>/', UpdateClassroomView.as_view(), name='api_close_classroom'),
    path('book-seat/', BookSeatView.as_view(), name='api_book_seat'),
    path('available-classrooms/', AvailableClassroomsView.as_view(), name='api_available_class_rooms'),
]