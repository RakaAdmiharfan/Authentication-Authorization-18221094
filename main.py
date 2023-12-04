from fastapi import FastAPI
from routes.requirements import getter_router, admin_router, friend_router
from routes.auth import auth_router
from jose import JWTError, jwt

app = FastAPI()
app.include_router(getter_router, prefix="/getters")
app.include_router(admin_router, prefix="/admin")
app.include_router(friend_router, prefix="/friend")
app.include_router(auth_router)  # Include the authentication router