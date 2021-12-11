# FastAPI for Digster API

# Activate virtual env
```sh
poetry shell
code .
```
# Run
## Locally
```sh
uvicorn main:app --reload
```
# Test
```sh
pytest --cov=digster_api tests -vv --cov-report html
```
# Migrate
```sh
alembic revision --autogenerate -m <your_commit_message>
alembic upgrade head
