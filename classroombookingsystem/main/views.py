from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from main.models import Classroom, Booking
from rest_framework.authentication import TokenAuthentication
from main.serializers import UserSerializer, ClassroomSerializer


# User Registration
class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    #render register page
    def get(self, request):
        return render(request, 'register_form.html')
    def post(self, request):
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            return render(request, 'registration_success.html', {'user': user})
        return render(request, 'registration_form.html', {'errors': serializer.errors})

#user login
class UserLoginView(ObtainAuthToken):
    #login page
    def get(self, request):
        return render(request, 'login_form.html')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            token = Token.objects.get(key=response.data['token'])
            # Store the token in session
            request.session['auth_token'] = token.key
            return render(request, 'login_success.html')

        return render(request, 'login_form.html', {'error': 'Invalid credentials'})

# User Dashboard
class DashboardView(APIView):
    def get(self, request):
        token_key = request.session.get('auth_token')
        print("--->",token_key)
        if token_key:
            try:
                classrooms = None
                token = Token.objects.get(key=token_key)
                user = token.user 
                print(user.role)
                if str(user.role).lower() == 'teacher':
                    classrooms = Classroom.objects.filter(teacher=user)
                else:
                    classrooms = Classroom.objects.filter(status='open')
                return render(request, 'dashboard.html', {'classrooms': classrooms})
            except Token.DoesNotExist:
                return redirect('login')
        else:
            return redirect('login') 


# Classroom Creation
class CreateClassroomView(APIView):
    def get(self, request):
        # Render the classroom creation form
        return render(request, 'classroom_form.html')

    def post(self, request):
        token_key = request.session.get('auth_token')
        print("--->",token_key)
        if token_key:
            try:
                classrooms = None
                token = Token.objects.get(key=token_key)
                user = token.user 
                print("role-->",user.role)
                if str(user.role).lower() != 'teacher':
                    return render(request, 'errors.html', {"detail": "Only teachers can create classrooms."})


                data_dict = {"teacher": user.id, "available_seats": request.POST['total_seats']}
                req_data = request.POST.copy()
                req_data.update(data_dict)
                print("req data-->", req_data)
                serializer = ClassroomSerializer(data=req_data)
                if serializer.is_valid():
                    classroom = serializer.save()
                    return render(request, 'classroom_details.html', {'classroom': classroom})
            except Token.DoesNotExist:
                return redirect('login') 
        else:
            return redirect('login') 
        


# Update Classroom Status
class UpdateClassroomView(APIView):

    def get(self, request, pk):
        token_key = request.session.get('auth_token')
        print("--->",token_key)
        if token_key:
            classroom = get_object_or_404(Classroom, pk=pk)
            token = Token.objects.get(key=token_key)
            user = token.user 
            if str(user.role).lower() != 'teacher':
                return render(request, 'errors.html', {"detail": "Only teachers can modify classrooms."})

            return render(request, 'classroom_form.html', {'classroom': classroom})
        else:
            return redirect('login') 

    def post(self, request, pk):
        token_key = request.session.get('auth_token')
        print("--->",token_key)
        if token_key:
            classroom = get_object_or_404(Classroom, pk=pk)
            token = Token.objects.get(key=token_key)
            user = token.user 
            if str(user.role).lower() != 'teacher':
                return render(request, 'errors.html', {"detail": "Only teachers can modify classrooms."})

            serializer = ClassroomSerializer(classroom, data=request.POST, partial=True)

            if serializer.is_valid():
                classroom = serializer.save()
                return render(request, 'classroom_details.html', {'classroom': classroom})

            return render(request, 'classroom_form.html', {'classroom': classroom, 'errors': serializer.errors})
        else:
            return redirect('login') 


#book seat
class BookSeatView(APIView):
    def post(self, request):
        token_key = request.session.get('auth_token')
        if not token_key:
            return redirect('login')  # Redirect to login if no token is found

        try:
            token = Token.objects.get(key=token_key)
            user = token.user

            if str(user.role).lower() != 'user':
                return render(request, 'errors.html', {"detail": "Only users can book seats."})

            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, pk=classroom_id, status='open')

            if classroom.available_seats > 0:
                # Book the seat
                Booking.objects.create(classroom=classroom, user=user)
                classroom.available_seats -= 1
                classroom.save()

                # Notify the teacher if the classroom is fully booked
                if classroom.available_seats == 0:
                    send_mail(
                        subject=f"Classroom {classroom.name} Fully Booked",
                        message=f"All seats in the classroom '{classroom.name}' have been booked.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[classroom.teacher.email],
                    )

                # Render the updated classroom list or details page
                classrooms = Classroom.objects.filter(status="open", available_seats__gte=1)
                return render(request, 'classroom_list.html', {
                    'classrooms': classrooms,
                    'success_message': f"You have successfully booked a seat in {classroom.name}."
                })
            else:
                return render(request, 'errors.html', {"detail": "No seats available."})

        except Token.DoesNotExist:
            return redirect('login')  # Redirect if token is invalid



# List Available Classrooms
class AvailableClassroomsView(APIView):
    def get(self, request):
        token_key = request.session.get('auth_token')
        if token_key:
            classrooms = Classroom.objects.filter(status="open", available_seats__gte=1)
            return render(request, 'classroom_list.html', {'classrooms': classrooms})
        else:
            return redirect('login') 


