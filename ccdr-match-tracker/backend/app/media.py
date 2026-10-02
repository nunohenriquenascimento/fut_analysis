"""Local public asset paths; no filesystem or binary storage in the API."""
import re
from typing import Annotated

from pydantic import AfterValidator, StringConstraints


def validate_asset_path(value: str) -> str:
    if not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.(?:png|jpg|jpeg|webp|avif|svg)", value):
        raise ValueError("Use um caminho público local como /players/jogador-8.webp.")
    return value


AssetPath = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500), AfterValidator(validate_asset_path)]
