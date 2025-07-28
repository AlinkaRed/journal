from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

import local_settings as ls


engine = create_engine(f"postgresql+psycopg2://{ls.DB_USER}:{ls.DB_PASSWORD}@{ls.DB_HOST}:{ls.DB_PORT}/{ls.DB_NAME}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
