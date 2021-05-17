from fabric.api import local


def bash(service):
    local(f'docker-compose exec {service} bash')


def runeventsapi():
    local(f'docker-compose run --rm --name crosswalk_eventsapi --service-ports --use-aliases eventsapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')
