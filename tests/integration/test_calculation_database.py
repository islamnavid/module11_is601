
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


@pytest.fixture(scope="module")
def db_engine():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    if not database_url.startswith(("postgresql://", "postgresql+")):
        pytest.fail("Integration tests require PostgreSQL")

    engine = create_engine(database_url)

    schema_name = f"module11_test_{uuid.uuid4().hex[:12]}"

    with engine.begin() as connection:
        connection.exec_driver_sql(
            f'CREATE SCHEMA "{schema_name}"'
        )

    schema_engine = engine.execution_options(
        schema_translate_map={None: schema_name}
    )

    try:
        Base.metadata.create_all(bind=schema_engine)
        yield schema_engine
    finally:
        Base.metadata.drop_all(bind=schema_engine)

        with engine.begin() as connection:
            connection.exec_driver_sql(
                f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'
            )

        engine.dispose()


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_user(db_session):
    unique = uuid.uuid4().hex

    user = User(
        username=f"test_{unique}",
        email=f"test_{unique}@example.com",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.mark.parametrize(
    "operation,inputs,expected,model_class",
    [
        ("addition", [10, 5], 15, Addition),
        ("subtraction", [10, 5], 5, Subtraction),
        ("multiplication", [10, 5], 50, Multiplication),
        ("division", [10, 5], 2, Division),
    ],
)
def test_calculation_persists_in_postgresql(
    db_session,
    test_user,
    operation,
    inputs,
    expected,
    model_class,
):
    # Save the user ID before detaching SQLAlchemy objects.
    user_id = test_user.id

    calculation = Calculation.create(
        calculation_type=operation,
        user_id=user_id,
        inputs=inputs,
    )

    calculation.result = calculation.get_result()

    db_session.add(calculation)
    db_session.commit()

    calculation_id = calculation.id

    # Clear the session to force a fresh database retrieval.
    db_session.expunge_all()

    stored = db_session.get(Calculation, calculation_id)

    assert stored is not None
    assert isinstance(stored, model_class)
    assert stored.user_id == user_id
    assert stored.type == operation
    assert stored.inputs == inputs
    assert stored.result == pytest.approx(expected)


def test_invalid_calculation_type():
    with pytest.raises(
        ValueError,
        match="Unsupported calculation type",
    ):
        Calculation.create(
            calculation_type="modulus",
            user_id=uuid.uuid4(),
            inputs=[10, 3],
        )


def test_division_by_zero():
    calculation = Calculation.create(
        calculation_type="division",
        user_id=uuid.uuid4(),
        inputs=[10, 0],
    )

    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculation.get_result()


def test_calculation_rejects_missing_user(db_session):
    calculation = Calculation.create(
        calculation_type="addition",
        user_id=uuid.uuid4(),
        inputs=[2, 3],
    )

    calculation.result = calculation.get_result()
    db_session.add(calculation)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
