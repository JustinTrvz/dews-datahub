import click
from backend import app


admin_group = None
user_group = None


@app.cli.command("init-db")
def init_db():
    """ Creates database tables for models specified at `backend/database/models.py` and user groups."""
    # Create DbClient object
    from backend.database.psql_client import PSQLClient as DbClient
    db_client = DbClient()

    # Drop tables
    ok = db_client.drop_db() 
    if ok:
        click.echo(f"Dropped database tables before creating new tables. url='{db_client.url}'")
    else:
        click.echo(f"Failed to drop database tables before creating new tables. Please try again! url='{DbClient.url}'")
        return

    # Create tables
    ok = db_client.init_db()
    if ok:
        click.echo(f"Created database tables. url='{db_client.url}'")
    else:
        click.echo(f"Failed to create database tables. Please try again! url='{DbClient.url}'")
        return

    # Create user groups
    from backend.database.models import DbUserGroup, DbUser
    _, admin_group = db_client.create(DbUserGroup, id="admin")
    _, user_group = db_client.create(DbUserGroup, id="user")
    click.echo(f"Created admin and user group. url='{db_client.url}'")

    # Create user
    user_id, _ = db_client.create(DbUser,
                                id="dews",
                                first_name="dews",
                                last_name="dews",
                                mail="dews@dews.de")
    if user_id is None:
        click.echo("Could not create 'dews' user. Please drop the database ('drop-db') and initialize again ('init-db')!")
        return
    
    # Get user
    queried_user = db_client.read(DbUser, user_id)
    if queried_user is None:
        click.echo(f"Failed to query 'dews' user. Please drop the database ('drop-db') and initialize again ('init-db')!")
    
    # Append groups
    queried_user.groups.append(user_group)
    queried_user.groups.append(admin_group)
    click.echo(f"Created default user 'dews'. url='{db_client.url}'")

    db_client.close_session()


@app.cli.command("drop-db")
def drop_db():
    """ Drops all model based tables that exist. """
    from backend.database.psql_client import PSQLClient as DbClient
    ok = DbClient.drop_db()
    if ok:
        click.echo(f"Dropped database. url='{DbClient.url}'")
    else:
        click.echo(f"Failed to drop database. Please try again! url='{DbClient.url}'")
