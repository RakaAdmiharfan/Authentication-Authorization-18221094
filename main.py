from fastapi import FastAPI
from routes.requirements import getter_router, admin_router, friend_router, support_router
from routes.auth import auth_router
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Setelan CORS untuk menerima permintaan dari semua domain
origins = ["*"]

# Tambahkan middleware CORS ke aplikasi
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(friend_router, prefix="/friend")
app.include_router(support_router, prefix="/support")
app.include_router(getter_router, prefix="/getters")
app.include_router(admin_router, prefix="/admin")
app.include_router(auth_router)  # Include the authentication router
