########################################################################################
# THIS FILE IS A TEMPLATE, DO NOT DIRECTLY MODIFY THIS FILE!!!                         #
# DUPLICATE THIS FILE AND RENAME IT TO 'environment.py'                                #
########################################################################################

# Generate a new secret key
# Enter in console:

# .\manage.py shell
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())

# Secret key
SECRET_KEY=''

# Debug mode
DEBUG=True

# Allowed hosts
# DO NOT LEAVE '*' IN PRODUCTION
ALLOWED_HOSTS=['*']

# Database settings
DATABASE_NAME='' # Name of your database
DATABASE_USER='' # Username for your database
DATABASE_PASSWORD='' # Password for your database
DATABASE_HOST='' # Name of the service defined in docker-compose.yml
DATABASE_PORT='' # Default port for PostgreSQL

# Other Django settings...

