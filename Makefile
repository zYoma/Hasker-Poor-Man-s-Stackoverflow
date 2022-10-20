#!make
include .env
export $(shell sed 's/=.*//' .env)

COMPOSE = docker-compose -f ${DOCKER_COMPOSE_FILE}
BASE_COMMAND = ${COMPOSE} run --rm ${SERVICE_NAME}
COMMAND = ${BASE_COMMAND}  /bin/bash -c


prod_up:
	${COMPOSE} up --build

prod_down:
	${COMPOSE} down

app_migrate:
	${COMMAND} 'python manage.py migrate'

app_shell:
	${COMMAND} 'python manage.py shell'

app_test:
	${COMMAND} 'python manage.py test'