from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import DataForm, UserInDB
from src.auth.services import get_current_user

UserInDBDep = Annotated[UserInDB, Depends(get_current_user)]
OAuth2PasswordRequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
DataFormDep = Annotated[DataForm, Form()]
