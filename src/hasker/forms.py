import re
from django import forms
from django.core.exceptions import ValidationError

from .models import Question


class AskQuestionForm(forms.ModelForm):
    question_tags = forms.CharField(
        label='Tags', max_length=20, widget=forms.TextInput(attrs={'class': "form-control"}))

    class Meta:
        model = Question
        fields = ('title', 'text', 'question_tags')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_question_tags(self):
        tags = self.cleaned_data['question_tags'].strip()
        if not re.match(r'^[a-z,\s]{3,20}$', tags):
            raise ValidationError('Недопустимые символы в тегах!')
        if len(tags.split(',')) > 3:
            raise ValidationError('Введите не более 3 тегов!')
        return tags
