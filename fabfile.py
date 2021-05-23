from fabric.api import local


def bash(service):
    local(f'docker-compose exec {service} bash')


def runeapi():
    local(f'docker-compose run --rm --name eventsapi --service-ports --use-aliases eventsapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def runmapi():
    local(f'docker-compose run --rm --name messagesapi --service-ports --use-aliases messagesapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def runrapi():
    local(f'docker-compose run --rm --name reactionsapi --service-ports --use-aliases reactionsapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def testeapi(path='.'):
    local(f'docker-compose run -e DATABASE_NAME=test --rm --use-aliases eventsapi poetry run pytest -s {path}')
