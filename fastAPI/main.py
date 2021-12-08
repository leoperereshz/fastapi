from typing import List, Optional, Set, Dict
from datetime import datetime, time, timedelta
from fastapi import Body, FastAPI, Cookie, Header, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID

app = FastAPI()

#------------------------------------------------------------------------------

class Image(BaseModel):
    url: HttpUrl #tipo exótico do pydantic, é um str modificado para URLs
    name: str

class Item(BaseModel):
    name: str
    description: Optional[str] = Field(None, title="The description of the item",
        max_length=300, example="A very nice Item")
    price: float = Field(..., gt=0, description="The price must be greater than zero", example=35.4)
    tax: Optional[float] = None
    is_offer: Optional[bool] = None
    tags: List[str] = []
    UniqueList: Set[str] = set()
    image: Optional[Image] = None  #cria uma substrutura no json
    tumbnails: Optional[List[Image]] = None #lista de subestrutura
    start_datetime: Optional[datetime] = Body(None),
    end_datetime: Optional[datetime] = Body(None),
    repeat_at: Optional[time] = Body(None),
    process_after: Optional[timedelta] = Body(None),

    #Para mostrar exemplos de saída nos campos do OpenAPI, pode usar example dentro dos Field() 
    #ou criar a classe abaixo agrupando todos eles em um único lugar. Nesse caso não precisa usar Field() nos campos.
    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }

class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str

class Log(BaseModel):
    title: str
    timestamp: datetime
    description: Optional[str] = None

#------------------------------------------------------------------------------

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

#**user_in.dict() = retorna um dicionario 'desenvelopado' com os dados do modelo, direto como chaves/Valores.
#senão cada campo do objeto user_in_db seria um user_dict["username"], user_dict["email"], etc.

#------------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"Hello": "World"}

#tags - cria uma subdivisão no OpenApi, agrupando os metodos com a mesma tag.

@app.get("/items/", response_model=List[Item], tags=["items"])
def read_items(ads_id: Optional[str] = Cookie(None), user_agent: Optional[str] = Header(None)):
    #headers geralmente usam '-', o que é inválido no python, então ele automaticamente converte para '_' para poder usar.
    return {"ads_id": ads_id, "User-Agent": user_agent}

@app.get("/elements/", tags=["items"], deprecated=True) #deprecated indica ao OpenApi que essa função está sendo descontinuada
async def read_elements():
    return [{"item_id": "Foo"}]

#summary e description permite incluir uma descrição nesse método no OpenApi.
#se a description for muito longa, pode usar da forma como foi feito no create_item logo abaixo.

@app.get("/items/{item_id}", tags=["items"], summary="Get an item",description="Get an item, but text longer" )
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

#response_model indica no OpenAPI o tipo de retorno, mas também vai converter os dados de saída para esse tipo,
#então se tiver campos a mais, o fastapi vai limitar o retorno à declaração do tipo Item.
#Se o retorno for lista, use response_model=List[Item].

#response_model_exclude_unset indica para não retornar campos que não foram preenchidos, mesmo que eles tenham valor default ou none.
#pode usar ainda response_model_exclude_defaults=True e response_model_exclude_none=True para configurar esse comportamento
@app.post("/items/", response_model=Item, response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED, tags=["items"], summary="Create an item", response_description="The created item")
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """

    return item

#nesse caso foi criado um tipo de saída diferente só para não retornar o objeto com as senhas do usuário.
#mesmo que a função retorne um objeto do tipo UserIn, o fastapi vai converter para UserOut antes de retornar.
#também é possível indicar response_model_exclude={"password"}, mas o recomendado é criar outra classe mesmo.
@app.post("/user/", response_model=UserOut, tags=["users"])
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved

@app.put("/items/{item_id}", tags=["items"])
async def update_item(
    item_id: int,   #parâmetro get. Ao invés de int poderia usar UUID.
    item: Item = Body(  #parâmetro json
        ...,
        embed=True,     #cria uma substrutura 'Item no json de entrada, ao invés de deixar tudo no 1o nível.
        example={       #vai mostrar um exemplo no OpenAPI
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    )
):

'''
Pode passar mais de um exemplo. O OpenAPI vai montar uma combo para o usuário escolher o exemplo.

examples={
    "normal": {
        "summary": "A normal example",
        "description": "A **normal** item works correctly.",
        "value": {
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    },
    "converted": {
        "summary": "An example with converted data",
        "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
        "value": {
            "name": "Bar",
            "price": "35.4",
        },
    },
    "invalid": {
        "summary": "Invalid data is rejected with an error",
        "value": {
            "name": "Baz",
            "price": "thirty five point four",
        },
    },
}

Poderia usar, por exemplo, para fornecer exemplos de como cadastrar um cliente CNPJ, CPF, estrangeiro.
'''


    results = {"item_id": item_id, "item": item}
    return results

@app.post("/offers/", response_model=Offer, tags=["offers"])
async def create_offer(offer: Offer):
    return offer

@app.post("/images/multiple/", tags=["images"])
async def create_multiple_images(images: List[Image]):
    return images

#caso não queira criar uma classe para receber o json, basta criar um dict
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):  #mesmo que a chave do json sempre será str, o pydantic irá converter para int
    return weights

@app.put("/log/{id}")
def update_item(id: str, log: Log):

    fake_db = {}

    #conversão para json. Se tiver data, o pydantic vai converter para texto.
    json_compatible_log_data = jsonable_encoder(log)
    fake_db[id] = json_compatible_log_data

    #se nesse caso enviar um objeto pela API faltando algum campo, e o registro já existe no banco de dados,
    #o registro vai manter o valor antigo e só atualizar os campos que o usuário mandou.
    #ver sobre body partial updates, para poder enviar só os campos que precisam atualizar https://fastapi.tiangolo.com/tutorial/body-updates/

#para rodar no terminal: uvicorn main:app --reload