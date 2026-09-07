import os
from dotenv import load_dotenv

load_dotenv()

USER_URL=os.getenv("USER_URL")
DATABASE_URL=os.getenv("DATABASE_URL")
