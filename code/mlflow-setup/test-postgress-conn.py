import os

import sqlalchemy
from dotenv import load_dotenv

load_dotenv()


os.environ["DB_USER"] = "mlflow-usr"
os.environ["DB_PASS"] = "mlflow-pass"
os.environ["DB_NAME"] = "mlflow-db"
os.environ["DB_PORT"] = "5432"
os.environ["PROJECT_ID"] = "uao-mlflow-intro"
os.environ["INSTANCE_HOST"] = "104.198.53.103"
os.environ["INSTANCE_NAME"] = "mlflow-postgres"

# https://cloud.google.com/docs/authentication/provide-credentials-adc
def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    db_host = os.environ["INSTANCE_HOST"]  # e.g. '
    postgres_instance_name = os.environ["INSTANCE_NAME"]
    unix_socket_path = f"cloudsql/{os.environ['PROJECT_ID']}:us-central1:{postgres_instance_name}"
    print(unix_socket_path)

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            host=db_host,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),

        # ...
    )
    print(pool.url)
    pool.connect()
    return pool



def connect_tcp_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a TCP connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_host = os.environ[
        "INSTANCE_HOST"
    ]  # e.g. '127.0.0.1' ('172.17.0.1' if deployed to GAE Flex)
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    db_port = os.environ["DB_PORT"]  # e.g. 5432

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=int(db_port),
            database=db_name,
        ),
        # ...
    )
    with pool.connect() as connection:
        print(connection)
    return pool



if __name__ == '__main__':
    print(connect_tcp_socket())
    print("Connection successful!")
    print(connect_unix_socket())
    print("Connection successful!")