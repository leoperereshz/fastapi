from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

#from . import crud, models, schemas
#from .database import SessionLocal, engine

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) #cria as tabelas. O ideal seria fazer com Alembic

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db    # O yield diz o que é dependência.
    finally:        # O finally é o que é executado quando o yield termina (depois que o create_user der return 
        db.close()  # garantindo que sempre vai fechar a sessão, mesmo se der exception.
                    # Como é executado depois que retornar, ele não consegue modificar o retorno do create_user).


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


#para executar
#uvicorn sql_app.main:app --reload