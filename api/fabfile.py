# flake8: noqa
from fabric.api import local


def bash():
    local(f"docker exec -ti api bash")


def run():
    local(
        f"docker-compose run --rm --name api --service-ports --use-aliases api poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    )


def runlocal():
    local(
        f"export DATABASE_HOST=apidb; poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    )


def test(path="."):
    local(
        f"docker-compose run -e TEST=1 --rm --use-aliases api poetry run pytest -s {path}"
    )


def lint(path="."):
    local(f"poetry run isort {path}")
    local(f"poetry run black {path}")
    local(f"poetry run flake8 {path}")
