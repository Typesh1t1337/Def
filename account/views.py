from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.views.generic import View


class RegisterView(View):
    template_name = 'index/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self,request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request,'Passwords must match')
        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already taken')

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already taken')

        user = User.objects.create_user(username=username,email=email,password=password)
        user.save()

        login(request,user)

        return redirect('index')

def logout_user(request):
    logout(request)
    return redirect('register')

class LoginView(View):
    template_name = 'index/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect('/')
        else:
            return redirect('login')



