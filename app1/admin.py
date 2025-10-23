from django.contrib import admin
from .models import Question, QuestionImage, Answer

class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 1  # show one empty upload slot by default

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'created_at')
    inlines = [QuestionImageInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'choice', 'submitted_at')
