from typing import List
from pydantic import BaseModel
from fastapi import FastAPI

class GraphList(BaseModel):
    data: List[GraphBase]