Alemebic Commands to run.

# 1. Make model changes (e.g., add a new column)

# 2. Create migration
alembic revision --autogenerate -m "add new column to users"

# 3. Apply migration
alembic upgrade head


# 4. If something breaks, rollback
alembic downgrade -1



