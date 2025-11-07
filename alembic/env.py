# import os
# import sys
# from logging.config import fileConfig

# from sqlalchemy import pool
# from sqlalchemy.engine import create_engine
# from alembic import context

# from dotenv import load_dotenv
# load_dotenv()

# # Step 1: Add Backend path to sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Step 2: Import Base and all models (so Alembic knows about them)
# from database import Base
# import models  # Must import all models

# # Step 3: Alembic config
# config = context.config

# # Step 4: Set DB URL dynamically from .env or directly
# config.set_main_option(
#     "sqlalchemy.url",
#     os.getenv("SUPABASE_DB")  # Or hardcoded string, if needed
# )

# # Step 5: Set up logging
# fileConfig(config.config_file_name)

# # Step 6: Metadata for 'autogenerate'
# target_metadata = Base.metadata

# # Step 7: Offline mode
# def run_migrations_offline():
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )
#     with context.begin_transaction():
#         context.run_migrations()

# # Step 8: Online mode
# def run_migrations_online():
#     engine = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)

#     with engine.connect() as connection:
#         context.configure(connection=connection, target_metadata=target_metadata)

#         with context.begin_transaction():
#             context.run_migrations()

# # Step 9: Mode switch
# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from dotenv import load_dotenv
load_dotenv()

import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base
from models import user
from models import query   # import all tables models from the model folder which inherits from the base 
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# ✅ Load DB URL from environment variable
database_url = os.getenv("SYNC_SUPABASE_DB")

if not database_url:
    raise ValueError("DATABASE_URL not found in environment. Please check your .env file.")

def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {
            'sqlalchemy.url': database_url
        },
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

