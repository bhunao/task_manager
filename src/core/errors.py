from fastapi import HTTPException, status


HTTP404_ITEM_NOT_FOUND = HTTPException(status_code=404, detail="Item not found")

HTTP500_DATABASE_ERROR = HTTPException(
    status_code=500, detail="Database Operational Error"
)

HTTP400_ALREADY_EXISTS = HTTPException(status_code=400, detail="Item already exists")

HTTP401_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
