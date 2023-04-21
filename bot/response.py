from typing import Any, Dict, NamedTuple, Optional
import typing

from bot.error import Error

SummarizeResponse = NamedTuple("SummarizeResponse", [("id", str), ("summary", str), ("meta", Optional[Dict[str, Any]])])
SummarizeResponse.__doc__ = """
    Берілген мәтін үшін көрсетілген ұзындықтың қорытындысын жасайтын summarize арқылы қайтарылады.
"""


def is_api_key_valid(key: typing.Optional[str]) -> bool:
    """is_api_key_valid кілт жарамды болғанда True мәнін қайтарады және ол жарамсыз болғанда Error мәнін береді."""
    if not key:
        raise Error(
            "API кілті берілмейді. Клиентті инициализациялауда API кілтін немесе CO_API_KEY ортасының айнымалы мәнін қамтамасыз етіңіз."
            # noqa: E501
        )
    return True

# сілтемелер
SUMMARIZE_URL = "summarize"
COHERE_API_URL = "https://api.cohere.ai"
COHERE_EMBED_BATCH_SIZE = 96
API_VERSION = "1"
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]