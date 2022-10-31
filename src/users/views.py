from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import UserRegistrationForm, UserSettingsForm


class Register(FormView):
    template_name = 'users/reg.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        new_user.refresh_from_db()

        return render(self.request, 'users/register_done.html', {'new_user': new_user})


class ProfileDetail(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('users:login')
    template_name = 'users/settings.html'
    form_class = UserSettingsForm
    success_url = reverse_lazy('hasker:index_url')

    def get_form(self, *args, **kwargs):
        return self.form_class(instance=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
