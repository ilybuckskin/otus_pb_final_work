import os


def get_environ(environ_name, default=None):
    result = os.getenv(environ_name, default=default)
    return result


def get_connection_string_bot() -> str:
    host = get_environ("DB_HOST_BOT")
    port = get_environ("DB_PORT_BOT")
    user = get_environ("DB_USER_BOT")
    database = get_environ("DB_NAME_BOT")
    passwd = get_environ("DB_PASS_BOT")
    return f"postgresql+psycopg://{user}:{passwd}@{host}:{port}/{database}"


def get_connection_string_dagster() -> str:
    host = get_environ("DAGSTER_POSTGRES_HOST")
    port = get_environ("DAGSTER_POSTGRES_PORT")
    user = get_environ("DAGSTER_POSTGRES_USER")
    database = get_environ("DAGSTER_POSTGRES_DB")
    passwd = get_environ("DAGSTER_POSTGRES_PASSWORD")
    return f"postgresql+psycopg://{user}:{passwd}@{host}:{port}/{database}"
