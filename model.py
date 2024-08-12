import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,  relationship, sessionmaker
from sqlalchemy import String, select, ForeignKey
import bcrypt
from flask import Flask
import uuid
import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

if not os.path.exists(instance_path):
    os.makedirs(instance_path)

db = sqlalchemy.create_engine(f"sqlite:///{os.path.join(instance_path, 'users.db')}")
Session = sessionmaker(bind=db)

class Base(DeclarativeBase): 
    pass

def generate_uuid():
    return str(uuid.uuid4())

class Credential(Base):
    __tablename__ = "credential"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)

    email_address: Mapped[str] = mapped_column(String(150), nullable=False, unique=False)
    hash_password: Mapped[bytes] = mapped_column(String(150), nullable=False, unique=False)


    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="credential")


    def __init__(self, email: str, password: str):
        self.email_address = email
        self.hash_password = (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(30), nullable=True, unique=True)

    credential: Mapped["Credential"] = relationship(back_populates="user", uselist=False)

    def __init__(self, username: str, credential=Credential):
        self.credential = credential
        self.username = username


    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"
    

def get_user_session(username: str):
    with Session() as session:
        user = session.execute(
        select(User)
        .where(User.username == username)
        .execution_options(populate_existing=True),
        ).scalar_one_or_none()

        if not user:
            return 
        credential = session.execute(
            select(Credential)
            .where(Credential.user_id == user.id)
            .execution_options(populate_existing=True)
        ).scalar_one_or_none()

        user.credential = credential
        return user;


        

def add_user_session(user: User):
    with Session() as session:
        session.add(user)
        session.commit()

def init(app: Flask) -> None:
    with app.app_context():
        db.connect()
        Base.metadata.create_all(db)