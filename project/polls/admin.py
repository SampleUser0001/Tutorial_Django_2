from django.contrib import admin

# Register your models here.

from .models import *

# ChoiceをQuestionと紐付ける
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('質問', {'fields': ['question_text']}),
        ('公開日', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]

    list_display = ('question_text', 'pub_date', 'was_published_recently')

    list_filter = ['pub_date']
    search_fields = ['questino_text']

admin.site.register(Question, QuestionAdmin)
