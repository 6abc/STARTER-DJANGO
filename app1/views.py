# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# # Create your views here.
# @login_required
# def app1(request):
#     return render(request, 'app1/app.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from .forms import AnswerForm

@login_required
def app_view(request):
    questions = Question.objects.all()

    if request.method == 'POST':
        form = AnswerForm(request.POST, questions=questions)
        if form.is_valid():
            for question in questions:
                choice_value = form.cleaned_data.get(f"question_{question.id}")
                Answer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'choice': choice_value}
                )
            return redirect('profile')
    else:
        form = AnswerForm(questions=questions)

    # attach field info for template use
    for q in questions:
        q.choices = form.fields[f"question_{q.id}"].choices

    return render(request, 'app1/app.html', {'form': form, 'questions': questions})