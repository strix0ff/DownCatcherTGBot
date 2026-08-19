import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    Header,
    Depends
)

from pydantic import ( 
    BaseModel
)

from api.config import (
    APIKEY
)

from api.core.database import (
    db_add,
    db_remove,
    db_getall
)

async def verify(x_api_key: str = Header(...)):
    if x_api_key != APIKEY:
        raise HTTPException(status_code=401, detail='Unauthorized request')

class AddService(BaseModel):
    address: str
    name: str

router = APIRouter(prefix='/service')

@router.post('/add')
async def service_add_handler(data: AddService, token: str = Depends(verify)):
    id = uuid.uuid4()
    await db_add(str(id), data.address, data.name)
    return {'message': 'Successful!'}

@router.delete('/{id}')
async def service_delete_handler(id: str, token: str = Depends(verify)):
    isdone = await db_remove(id)
    if isdone == None:
        raise HTTPException(status_code=404, detail='This service id is not found')
    else:
        return {'message': 'Successful!'}

@router.get('/get')
async def service_get_handler(token: str = Depends(verify)):
    return await db_getall()
