# OLD
# FROM python:3.9
# WORKDIR /code
# COPY ./requirements.txt /code/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# COPY ./fastapiDocker /code/fastapiDocker
# CMD ["uvicorn", "fastapiDocker,main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]


#Cria um estágio temporário só para gerar o requirements.txt do poetry
FROM python:3.9 as requirements-stage 
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.9 
WORKDIR /code
#copia o requirements.txt do container temporário e instala ele. Depois disso aquele container é destruído.
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "fastapiDocker.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]