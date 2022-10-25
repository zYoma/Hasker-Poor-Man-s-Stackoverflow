from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View

from .forms import UserRegistrationForm, UserSettingsForm


class Register(View):

    def post(self, request):
        user_form = UserRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_user.refresh_from_db()

            return render(request, 'users/register_done.html', {'new_user': new_user})
        return render(request, 'users/reg.html', {'user_form': user_form})

    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'users/reg.html', {'user_form': user_form})


class Settings(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    template_name = 'users/settings.html'

    def post(self, request):
        user_form = UserSettingsForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('hasker:index_url')
        return render(request, 'users/settings.html', {'user_form': user_form})

    def get(self, request):
        user_form = UserSettingsForm(instance=request.user)
        return render(request, 'users/settings.html', {'user_form': user_form})
