from django.core.management import call_command
from django.db import connection


def test_system_check_passes() -> None:
    call_command("check", fail_level="WARNING")


def test_database_is_postgres_test_db(db: None) -> None:
    assert connection.vendor == "postgresql"
    assert connection.settings_dict["NAME"] == "oqf_test"
