from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .models.user import User
from .utils.hashing import get_password_hash


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        test_admin = session.get(User, "test")
        if test_admin:
            return
        test_admin = User(username="test", is_admin=True, balance=10000)
        test_admin.password = get_password_hash("test")
        session.add(test_admin)
        session.commit()
        session.refresh(test_admin)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]