"""
Run ONCE after adding the new models to create the v3 tables.
This is additive: it creates document_chunks, entities, and relationships.
It does NOT touch or drop your existing `documents` table or its data.

    (venv) > python create_tables.py
"""

from database import engine, Base
import models  # noqa: F401  (importing registers all model classes on Base)

Base.metadata.create_all(bind=engine)
print("v3 tables ensured: document_chunks, entities, relationships")