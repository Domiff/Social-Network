from fastapi import HTTPException

username_already_taken = HTTPException(status_code=400, detail="Username already taken")
incorrect_credentials = HTTPException(status_code=400, detail="Incorrect credentials")
unauthorized = HTTPException(status_code=401, detail="Unauthorized")
expired_signature = HTTPException(status_code=401, detail="Token expired")
invalid_token = HTTPException(status_code=401, detail="Token is invalid")
