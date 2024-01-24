from database import Client, Bill, Session, Model, Transaction, Base

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta

#Database path
SQLALCHEMY_DATABASE_URL = "sqlite:///users.db"  

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Secret key to encode and decode JWT tokens
SECRET_KEY = "610638D4E5CF4AC7F457C0AA7A3E7D30CA1B0E11026E7523DFC5DBEE8D2F1CDE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, username: str):
    return db.query(Client).filter(Client.Email == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.Password):
        return False
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/select-model/")
async def select_model(model_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_email = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    client = db.query(Client).filter(Client.Email == user_email).first()
    model = db.query(Model).filter(Model.ModelID == model_id).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Check that user has enough Coins
    bill = db.query(Bill).filter(Bill.ClientID == client.ClientID).first()
    if bill.Coins < model.Cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Deduct Cfoins 
    bill.Coins -= model.Cost
    db.commit()

    # Return model selection, coins
    return {"model_selected": model.ModelName, "remaining_coins": bill.Coins}

@app.post("/upload-data/")
async def upload_data(file: UploadFile, model_id: int): 
    # 
    # Add the task to the queue
    job_id = add_task_to_queue(out_file_path, model_id)
    return {"message": "File uploaded and task created", "task_id": job_id}


#@app.get("/download-result/")
#async def download_result(task_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
Base.metadata.create_all(bind=engine)
