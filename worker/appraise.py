import asyncio
from pydantic import BaseModel
from random import *

class Appraisal(BaseModel):
    sickles: int
    galleons: int
    knuts: int

def appraise() -> Appraisal:
    # Work takes time
    asyncio.sleep(randint(0, 5))
    return Appraisal(sickles=randint(0, 10000),
                     galleons=randint(0, 1000),
                     knuts=randint(0, 100000)
                     )
    
