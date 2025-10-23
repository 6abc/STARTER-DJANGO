from django.db import models
from django.conf import settings


class Question(models.Model):
    text = models.TextField()
    help_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]


class QuestionImage(models.Model):
    """Each Question can have multiple uploaded images."""
    question = models.ForeignKey(Question, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="question_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Q{self.question.id}"


class Answer(models.Model):
    CHOICES = [
        (1, 'Regularly'),
        (2, 'Very Often'),
        (3, 'Every Day'),
        (4, 'Sometimes'),
        (5, 'Often'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.PositiveSmallIntegerField(choices=CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')  # each user answers each question once

    def __str__(self):
        return f"{self.user.username} → Q{self.question.id}: {self.get_choice_display()}"
