from src.model.db.config import get_engine
from src.model.db.models import Base


async def init_db() -> None:
    Base.metadata.create_all(get_engine())
