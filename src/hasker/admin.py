from django.contrib import admin

from .models import Answer, Tag, Question


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_date', 'is_correct_answer']
    search_fields = ['author', ]


admin.site.register(Answer, AnswerAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', ]


admin.site.register(Tag, TagAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_date']
    search_fields = ['author', 'title']


admin.site.register(Question, QuestionAdmin)
