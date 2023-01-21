# Sqlalchemy models for handling oauth tokens
# Must use type hints!
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    token = Column(String(255))
    refresh_token = Column(String(255))


def create_tables(engine):
    Base.metadata.create_all(engine)


# type hinted function for adding a user to the database
def add_user(
    session: Session,
    name: str,
    token: str,
    refresh_token: str,
) -> None:
    user = User(name=name, token=token, refresh_token=refresh_token)
    session.add(user)
    session.commit()
    session.close()


def get_user(session: Session, name: str) -> User:
    user = session.query(User).filter_by(name=name).first()
    session.close()
    return user


def update_user(session: Session, name: str, token: str, refresh_token: str) -> None:
    user = get_user(session, name)
    user.token = token
    user.refresh_token = refresh_token
    session.commit()
    session.close()


def main():
    # setup sqlite database
    engine = create_engine("sqlite:///test.db")
    create_tables(engine)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    add_user(session, "test", "token", "refresh_token")
    user = get_user(session, "test")
    print(user.name, user.token, user.refresh_token)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
