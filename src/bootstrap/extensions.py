from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.bootstrap.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=settings.rate_limit_storage_uri,
)
