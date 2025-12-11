# File: adidas_rag/__init__.py
try:
    # First try relative import (works when package is properly installed)
    from .rag_pipeline import (
        load_or_create_db,
        load_csv_as_documents,
        build_vector_db,
        search_db
    )
except ImportError:
    # Fallback to absolute import
    from rag_pipeline import (
        load_or_create_db,
        load_csv_as_documents,
        build_vector_db,
        search_db
    )

__all__ = [
    "load_or_create_db",
    "load_csv_as_documents",
    "build_vector_db",
    "search_db"
]