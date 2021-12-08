from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()

#para casos em que os campos precisam ir como formulários, ex: Oauth2 username e password
#formulários geralmente são codificados de forma diferente que um json. ex: application/x-www-form-urlencoded
#quando inclui arquivos, geralmente é multipart/form-data

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

#ao usar o tipo bytes, o File() irá ler o conteúdo e armazenar em memória.
#não permite ler os metadados do arquivo.

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}

#ao usar a classe UploadFile, será criado um arquivo em memória até certo limite,
#ou se passar disso irá criar um arquivo em disco (SpooledTemporaryFile), sem consumir a memória.
#também permite obter os metadados do arquivo.
#oferece métodos assíncronos como file.write(data), file.read(size), file.close(), file.seek(offset) para levar o cursor até um ponto específico do arquivo

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await myfile.read()
    contents = myfile.file.read() #síncrono
    return {"filename": file.filename}


#upload de múltiplos arquivos

@app.post("/images/")
async def create_images(images: List[bytes] = File(...)):
    return {"file_sizes": [len(image) for image in images]}


@app.post("/uploadimages/")
async def create_upload_images(images: List[UploadFile] = File(...)):
    return {"filenames": [image.filename for image in images]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/images/" enctype="multipart/form-data" method="post">
<input name="images" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadimages/" enctype="multipart/form-data" method="post">
<input name="images" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


#é possível usar files e Form Fields ao mesmo tempo, mas não é possível usar body (json) junto, por limitação do protocolo HTTP.
@app.post("/logos/")
async def create_logos(
    file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

