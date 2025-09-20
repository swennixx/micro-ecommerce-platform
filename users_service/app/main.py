
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, crud, deps, auth
from app.database import engine
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Users Service")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = structlog.get_logger()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

user_registered = Counter('user_registered_total', 'Total registered users')
user_login = Counter('user_login_total', 'Total user logins')

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/register", response_model=schemas.UserRead)
@limiter.limit("10/minute")
async def register(request: Request, user: schemas.UserCreate, db: AsyncSession = Depends(deps.get_db)):
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_obj = await crud.create_user(db, user)
    if not user_obj:
        raise HTTPException(status_code=400, detail="Registration failed")
    user_registered.inc()
    logger.info("user_registered", username=user.username)
    return user_obj

@app.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(deps.get_db)):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    user_login.inc()
    logger.info("user_login", username=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(current_user=Depends(deps.get_current_active_user)):
    return current_user

@app.get("/users/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(deps.get_db), current_user=Depends(deps.get_current_admin_user)):
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
