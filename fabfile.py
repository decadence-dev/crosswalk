from fabric.api import local


def bash(service):
    local(f'docker-compose exec {service} bash')


def runapi():
    local(f'docker-compose run --rm --name events --service-ports --use-aliases events poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def runmapi():
    local(f'docker-compose run --rm --name messagesapi --service-ports --use-aliases messagesapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def runrapi():
    local(f'docker-compose run --rm --name reactionsapi --service-ports --use-aliases reactionsapi poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def testapi(path='.'):
    local(f'docker-compose run -e DATABASE_NAME=test --rm --use-aliases events poetry run pytest -s {path}')


def testmapi(path='.'):
    local(f'docker-compose run -e DATABASE_NAME=test --rm --use-aliases messagesapi poetry run pytest -s {path}')
