from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
engine = create_engine('sqlite:///premiumassests1.db')


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
