from fabric.api import local


def bash(service):
    local(f'docker-compose exec {service} bash')


def runapi():
    local(f'docker-compose run --rm --name api --service-ports --use-aliases api poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def testapi(path='.'):
    local(f'docker-compose run -e DATABASE_NAME=test --rm --use-aliases api poetry run pytest -s {path}')
