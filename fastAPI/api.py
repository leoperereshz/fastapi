import uvicorn #diferente do Flask, o FastAPI não tem um web server embutido
import random
from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel
from typing import Optional

class Application(BaseModel):
    first_name: str
    last_name: str
    age: int
    degree: str
    interest: Optional[str] = None

class Decision(BaseModel):
    first_name: str
    last_name: str
    probability: float
    acceptance: bool


app = FastAPI()

async def some_blocking_operation():
    # I/O read or write
    # a remote API call
    # database read and write
    # ...
    pass

#Assync
app.get("/")
async def read_results():
    results = await some_blocking_operation()
    
    # other computations 
    # ...
    
    return results

@app.get("/employee/{id}")
def home(id: int):
    return {"id": id}

@app.post("/")
def home_post():
    return {"Hello": "POST"}

#Pydantic
@app.post("/applications", response_model=Decision)
async def create_application(id: int, application: Application):

    first_name = application.first_name
    last_name = application.last_name
    proba = random.random()
    acceptance = proba > 0.5

    decision = {
        "first_name": first_name,
        "last_name": last_name,
        "probability": proba,
        "acceptance": acceptance,
    }
    return decision

#String validations
@app.get("/items/")
async def read_items(q: Optional[str] = Query(None, max_length=50, min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q: 
        results.update({"q": q})
    return results

# @app.get("/items/{item_id}")
# async def read_items(*, item_id: int == Path(..., title="The ID of the item to get"), gt=0, le=1000, q: str):
#     results = {"item_id": item_id}
#     if q: 
#         results.update({"q": q})
#     return results


#Error Handling
students = {
  1235: "Bobby Fischer", 
  252: "Alice Mcqueen"
}

@app.get("/students/{student_id}")
async def read_student_id(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student ID not found")
    return {"student": students[student_id]}

if __name__ == "__main__":
    uvicorn.run("api:app")

    #auto doc: http://localhost:8000/docs
