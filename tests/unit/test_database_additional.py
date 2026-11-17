
from unittest.mock import MagicMock, patch

from sqlalchemy import text

from app.database import (
    get_db,
    get_engine,
    get_sessionmaker,
)


def test_get_db_closes_session():
    mock_session = MagicMock()

    with patch(
        "app.database.SessionLocal",
        return_value=mock_session,
    ):
        generator = get_db()
        session = next(generator)

        assert session is mock_session

        try:
            next(generator)
        except StopIteration:
            pass
        else:
            raise AssertionError(
                "Database dependency should yield only once"
            )

        mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception():
    mock_session = MagicMock()

    with patch(
        "app.database.SessionLocal",
        return_value=mock_session,
    ):
        generator = get_db()
        next(generator)

        try:
            generator.throw(
                RuntimeError("Simulated database failure")
            )
        except RuntimeError:
            pass

        mock_session.close.assert_called_once()


def test_get_engine():
    engine = get_engine("sqlite:///:memory:")

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            ).scalar()

        assert result == 1
    finally:
        engine.dispose()


def test_get_sessionmaker():
    engine = get_engine("sqlite:///:memory:")

    try:
        session_factory = get_sessionmaker(engine)
        session = session_factory()

        try:
            assert session.bind is engine
            assert session.autoflush is False
        finally:
            session.close()
    finally:
        engine.dispose()
