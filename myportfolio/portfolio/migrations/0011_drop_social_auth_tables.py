# Cleans up after removing social_django (python-social-auth) from
# INSTALLED_APPS. Its tables, migration records, content types and
# permissions are left behind otherwise. Safe to run on databases that
# never had social_django installed.

from django.db import migrations

SOCIAL_AUTH_TABLES = [
    'social_auth_usersocialauth',
    'social_auth_association',
    'social_auth_code',
    'social_auth_nonce',
    'social_auth_partial',
]


def drop_social_auth(apps, schema_editor):
    connection = schema_editor.connection
    existing = set(connection.introspection.table_names())
    for table in SOCIAL_AUTH_TABLES:
        if table in existing:
            schema_editor.execute(f'DROP TABLE {schema_editor.quote_name(table)}')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations WHERE app = %s", ['social_django'])

    # Deleting the content types also removes their permissions (cascade)
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.using(connection.alias).filter(app_label='social_django').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0010_alter_blogpost_category_alter_blogpost_title'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('admin', '0003_logentry_add_action_flag_choices'),
    ]

    operations = [
        migrations.RunPython(drop_social_auth, migrations.RunPython.noop),
    ]
