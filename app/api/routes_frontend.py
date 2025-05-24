from fastapi import APIRouter, Request, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import timedelta
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import get_password_hash, create_access_token
from app.db.database import SessionLocal
from app.models.user import User
import secrets
from app.db.crud import verify_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    csrf_token = secrets.token_urlsafe(16)
    response = templates.TemplateResponse("login.html", {"request": request, "csrf_token": csrf_token})
    response.set_cookie("csrf_token", csrf_token)
    return response

@router.post("/")
def login_user_from_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...)
):
    csrf_cookie = request.cookies.get("csrf_token")
    if csrf_token != csrf_cookie:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный CSRF токен"
        })

    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username).first()

        if not user or not verify_password(password, user.hashed_password):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    response = RedirectResponse("/upload", status_code=status.HTTP_302_FOUND)
    response.set_cookie("access_token", access_token, httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    csrf_token = secrets.token_urlsafe(16)
    response = templates.TemplateResponse("register.html", {"request": request, "csrf_token": csrf_token})
    response.set_cookie("csrf_token", csrf_token)
    return response

@router.post("/register")
def register_user_from_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...)
):
    csrf_cookie = request.cookies.get("csrf_token")
    if csrf_token != csrf_cookie:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Неверный CSRF токен"
        })

    if len(password) < 8:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Пароль должен быть не короче 8 символов"
        })

    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})

    new_user = User(
        username=username,
        hashed_password=get_password_hash(password),
        requests_left=20
    )
    db.add(new_user)
    db.commit()

    return RedirectResponse("/", status_code=302)

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/", status_code=302)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse("upload.html", {"request": request})

@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response
