from pathlib import Path

import mysql.connector

from src.DatabaseConfig import DatabaseConfig


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def connect():
    config = DatabaseConfig.from_docker_secrets(
        host="db",
        user="hello",
        database="helloapp",
        password_key="db_user_password",
    )

    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database,
    )


def ensure_migrations_table(db) -> None:
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    db.commit()
    cursor.close()


def get_applied_migrations(db) -> set[str]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT version
        FROM schema_migrations
        """
    )

    versions = {row[0] for row in cursor.fetchall()}

    cursor.close()

    return versions


def apply_migration(db, migration_file: Path) -> None:
    version = migration_file.stem.split("_", 1)[0]

    sql = migration_file.read_text(encoding="utf-8")

    print(f"Applying migration {version}: {migration_file.name}")

    cursor = db.cursor()

    try:
        cursor.execute(sql)

        cursor.execute(
            """
            INSERT INTO schema_migrations (version)
            VALUES (%s)
            """,
            (version,),
        )

        db.commit()

        print(f"Migration {version} applied successfully")

    except Exception:
        db.rollback()
        print(f"Migration {version} failed")
        raise

    finally:
        cursor.close()


def main() -> None:
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        print("No migrations found")
        return

    db = connect()

    try:
        ensure_migrations_table(db)

        applied = get_applied_migrations(db)

        for migration_file in migration_files:
            version = migration_file.stem.split("_", 1)[0]

            if version in applied:
                print(f"Migration {version} already applied")
                continue

            apply_migration(db, migration_file)

    finally:
        db.close()


if __name__ == "__main__":
    main()
