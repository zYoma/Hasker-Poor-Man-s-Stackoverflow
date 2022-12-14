# Generated by Django 4.1.2 on 2022-10-18 14:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hasker', '0002_answer_rating_useranswerrating'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuestionRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='rating',
            field=models.IntegerField(default=0, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=10, unique=True, verbose_name='Название тега'),
        ),
        migrations.AddConstraint(
            model_name='useranswerrating',
            constraint=models.UniqueConstraint(fields=('user', 'answer'), name='unique_user_answer_rating'),
        ),
        migrations.AddField(
            model_name='userquestionrating',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_ratings', to='hasker.question', verbose_name='Вопрос'),
        ),
        migrations.AddField(
            model_name='userquestionrating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_ratings', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='userquestionrating',
            constraint=models.UniqueConstraint(fields=('user', 'question'), name='unique_user_question_rating'),
        ),
    ]
