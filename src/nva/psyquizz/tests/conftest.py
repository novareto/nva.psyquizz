from nva.psyquizz import Base
import pytest


@pytest.fixture(scope='session')
def engine():
    from cromlech.sqlalchemy import create_and_register_engine

    return create_and_register_engine('sqlite:////tmp/quizz.db', 'school')


@pytest.yield_fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(engine.engine)
    yield
    Base.metadata.drop_all(engine.engine)


@pytest.yield_fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    from cromlech.sqlalchemy import get_session
    from cromlech.sqlalchemy import SQLAlchemySession
    with SQLAlchemySession(engine) as session:
        yield session
    session.rollback()
    session.close()
