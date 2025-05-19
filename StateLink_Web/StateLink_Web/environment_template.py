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
SECRET_KEY='7x7g=26w4-shn1!&a&@19+2(@uca@08n+1-%g@+87nh32p@@_8'

# Debug mode
DEBUG=True

# Allowed hosts
# DO NOT LEAVE '*' IN PRODUCTION
ALLOWED_HOSTS=[
    'your-domain.com',
    'www.your-domain.com',
    'subdomain.your-domain.com',
    'statelink-webapp.azurewebsites.net'
]

# Database settings
DATABASE_NAME='' # Name of your database
DATABASE_USER='' # Username for your database
DATABASE_PASSWORD='' # Password for your database
DATABASE_HOST='' # Name of the service defined in docker-compose.yml
DATABASE_PORT='' # Default port for PostgreSQL

# Other Django settings...

