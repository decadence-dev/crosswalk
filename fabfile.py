from fabric.api import local


def bash(service):
    local(f'docker-compose exec {service} bash')


def runapi():
    local(f'docker-compose run --rm --name events --service-ports --use-aliases events poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload')


def testapi(path='.'):
    local(f'docker-compose run -e DATABASE_NAME=test --rm --use-aliases events poetry run pytest -s {path}')
