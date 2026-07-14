# Generated migration for security fix

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0003_alter_oauthuser_nickname'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='oauthuser',
            unique_together={('type', 'openid')},
        ),
    ]
