from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.shortcuts import render, redirect


class EditProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = (
            
            "first_name",
            "last_name",
            "email",
        )


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request,"register.html", {'form': form})

def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)
        print(form)
        args = {'form':form}
        return render(request,'edit_profile.html', {'form': form})