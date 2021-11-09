from pydantic import BaseSettings


class Settings(BaseSettings):
    auth_expiration_minutes: int = 60
    debug: bool = True
    secret_key: str = "secret"
    actions_topic: str = 'events-actions'
    bootstrap_servers: list =['kafka:9092']
    database_host: str = "localhost"
    database_port: int = 27017
    database_name: str = "crosswalk"
    global_limit: int = 100
    origins: list = ["*"]

settings = Settings()
