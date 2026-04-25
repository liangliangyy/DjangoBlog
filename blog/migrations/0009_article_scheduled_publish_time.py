from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_blogsettings_color_scheme'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='scheduled_publish_time',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='If set, the article will be automatically published at this time. Can be set for both draft and published articles.',
                verbose_name='scheduled publish time'
            ),
        ),
    ]
