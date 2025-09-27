from app.config.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, PasswordReset, UserResponse
from app.utils.auth import hash_password, verify_password, create_access_token, verify_token
from app.utils.mail import send_email_verification, password_reset_mail

from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import or_
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/users',
    tags=['users']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')


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
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token'
        )        

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    user.is_verified = True
    db.commit()

    return {'message': 'Email verification successful'}


@router.post('/login', status_code=status.HTTP_200_OK)
async def user_login(
    body: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == body.username).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password'
        )
    
    access_token = create_access_token(
        data={'sub':user.username}
    )

    return Token(access_token=access_token, token_type='Bearer')


@router.post('/forgot-password', status_code=status.HTTP_200_OK)
async def forgot_password(
    body: PasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    token = create_access_token({'sub':user.email})

    base_url = str(request.base_url).rstrip('/')
    link = f'{base_url}/users/reset-password?token={token}'

    background_tasks.add_task(password_reset_mail, user.email, user.full_name, link)

    return {'message':'Password reset mail sent'}


@router.put('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(
    token: str,
    new_pwd: str = Form(...),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token'
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    user.password = hash_password(new_pwd)
    db.commit()

    return {'message': 'Password reset successful'}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(
        or_(User.username == username, User.email == username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user

@router.get('/me', status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user