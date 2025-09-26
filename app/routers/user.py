from app.config.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token
from app.utils.auth import hash_password, verify_password, create_access_token, verify_token
from app.utils.mail import send_email_verification

from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks, Request

from sqlalchemy import or_
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(
    body: UserCreate, 
    background_tasks: 
    BackgroundTasks, 
    request: Request,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        or_(User.email == body.email, User.username == body.username)
    ).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this username or email already exists'
        )
    
    hashed_password = hash_password(body.password)

    new_user = User(
        full_name=body.full_name,
        email=body.email,
        username=body.username,
        phone_number=body.phone_number,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({'sub':new_user.email})

    base_url = str(request.base_url).rstrip('/')
    link = f'{base_url}/users/verify-email?token={token}'

    background_tasks.add_task(
        send_email_verification, 
        new_user.email, 
        new_user.full_name, 
        link=link
    )

    return new_user


@router.get('/verify-email', status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    email = verify_token(token)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token'
        )
    
    user.is_verified = True
    db.commit()

    return {'message': 'Email verification successful'}


@router.post('/login', status_code=status.HTTP_200_OK)
async def user_login(
    body: UserLogin, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password'
        )
    
    access_token = create_access_token(
        data={'sub':user.username}
    )

    return Token(access_token=access_token, token_type='Bearer')

