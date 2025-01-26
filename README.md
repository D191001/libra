# FastAPI Application

##




# Cоздание миграции

docker-compose exec web alembic revision --autogenerate -m "Initial migration"

# Применить миграции:
docker-compose exec web alembic upgrade head