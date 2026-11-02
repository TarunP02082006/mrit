from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect_by_role(user)
        else:
            error = "Invalid username or password. Please try again."

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def redirect_by_role(user):
    if user.is_admin_role():
        return redirect('admin_dashboard')
    elif user.is_supervisor_role():
        return redirect('supervisor_dashboard')
    else:
        return redirect('engineer_dashboard')


@login_required
def home_router(request):
    return redirect_by_role(request.user)


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role():
        return render(request, '403.html', {'message': 'Administrator access required.'}, status=403)
    return render(request, 'admin_dashboard.html', {'user': request.user})


@login_required
def engineer_dashboard(request):
    return render(request, 'engineer_dashboard.html', {'user': request.user})


@login_required
def supervisor_dashboard(request):
    if not request.user.is_supervisor_role():
        return render(request, '403.html', {'message': 'Supervisor access required.'}, status=403)
    return render(request, 'supervisor_dashboard.html', {'user': request.user})


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "is_admin": request.user.is_admin_role(),
            "is_engineer": request.user.is_engineer_role(),
            "is_supervisor": request.user.is_supervisor_role(),
        })
