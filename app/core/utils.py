from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Callable

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def skip_depend_in_docs(dep: Callable):
    async def wrapper(request: Request, token: str = Depends(oauth2_scheme)):
        if request.scope.get("openapi"):
            return None
        return await dep(token)
    return Depends(wrapper)

