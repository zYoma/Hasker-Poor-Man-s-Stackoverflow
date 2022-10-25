from django.contrib import admin

from .models import Answer, Question, Tag


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_date', 'is_correct_answer']
    search_fields = ['author']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_date']
    search_fields = ['author', 'title']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, AnswerAdmin)
