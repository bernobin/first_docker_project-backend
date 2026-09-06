from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    host: str
    user: str
    database: str
    password: str

    @classmethod
    def from_docker_secrets(
        cls,
        host: str,
        user: str,
        database: str,
        password_key: str,
    ) -> "DatabaseConfig":
        """Factory method to load secrets from /run/secrets/."""
        with open(f"/run/secrets/{password_key}", "r") as f:
            password = f.read().strip()

        return cls(host=host, user=user, database=database, password=password)
