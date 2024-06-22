from starlette.config import Config
from jinja2_fragments.fastapi import Jinja2Blocks

config = Config(".env")
templates = Jinja2Blocks(directory="src/template/")

SECRET_KEY = config("SECRET_KEY", default="DEFAULT_KEY")
ALGORITHM = config("ALGORITHM", cast=str, default="HS256")
