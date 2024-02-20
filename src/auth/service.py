from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from src.auth.utils import get_secrets

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
secrets = get_secrets()


def api_key_auth(token: str = Depends(oauth2_scheme)):
    """
    authentication function
    :param token: Bearer token
    """
    try:
        payload = jwt.decode(token, key=secrets['api_tokens']['service'], algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
