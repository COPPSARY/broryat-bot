from sqlalchemy import inspect

from bot.database.engine import create_db_and_tables, get_engine


def test_get_engine_connects_to_the_given_database_url():
    engine = get_engine("sqlite://")
    with engine.connect() as conn:
        assert conn is not None


def test_create_db_and_tables_creates_scan_records_table():
    engine = get_engine("sqlite://")

    create_db_and_tables(engine)

    assert "scan_records" in inspect(engine).get_table_names()
