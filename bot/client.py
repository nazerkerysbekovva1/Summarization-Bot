import json as jsonlib
import os
import time
import typing
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from bot.error import APIError, Error, ConnectionError
from bot.response import is_api_key_valid, SummarizeResponse, SUMMARIZE_URL, RETRY_STATUS_CODES, COHERE_API_URL, \
    COHERE_EMBED_BATCH_SIZE, API_VERSION


class Client:
    """Cohere Client

    Args:
        api_key (str): Сіздің API кілтіңіз.
         num_workers (int): параллельді шақырулар үшін ағындардың ең көп саны.
         request_dict (dict): сұраулар кітапханасы бар қоңырауларға арналған қосымша параметрлер.
         check_api_key (bool): инициализация кезінде api кілтінің жарамдылығын тексеру .
         client_name (str): Ішкі талдау мақсаттары үшін қолданбаны анықтауға арналған жол.
         max_retries (int): сұраулар үшін қайталау әрекеттерінің максималды саны.
        timeout (int): секундтарда күту уақытын сұрау.
    """

    def __init__(
            self,
            api_key: str = None,
            num_workers: int = 64,
            request_dict: dict = {},
            check_api_key: bool = True,
            client_name: Optional[str] = None,
            max_retries: int = 3,
            timeout: int = 120,
    ) -> None:
        self.api_key = api_key or os.getenv("CO_API_KEY")
        self.api_url = COHERE_API_URL
        self.batch_size = COHERE_EMBED_BATCH_SIZE
        self._executor = ThreadPoolExecutor(num_workers) # Сұрауларды параллельдеу үшін ThreadPoolExecutor.
        self.num_workers = num_workers
        self.request_dict = request_dict  # запростарды жіберу үшін қосымша параметрлер сөздігі
        self.request_source = "python-sdk"  # запростардың источнигі (мысалы, «python-sdk»).
        self.max_retries = max_retries
        self.timeout = timeout
        self.api_version = f"v{API_VERSION}"
        if client_name:
            self.request_source += ":" + client_name

        if check_api_key:
            self.check_api_key()

    def check_api_key(self) -> Dict[str, bool]:
        """
         (Client) клиентті инициализациялау кезінде автоматты түрде орындалатын api кілтін тексереді.
         check_api_key кілт жарамсыз болғанда қате жағдайды тудырады, бірақ жарамды кілттердің
         қайтару мәні келесі кодтар үшін сақталады.
        """
        return {"valid": is_api_key_valid(self.api_key)}

    def summarize(
            self,
            text: str,
            model: Optional[str] = None,
            length: Optional[str] = None,
            format: Optional[str] = None,
            temperature: Optional[float] = None,
            additional_command: Optional[str] = None,
            extractiveness: Optional[str] = None,
    ) -> SummarizeResponse:
        """Берілген мәтін үшін көрсетілген ұзындықтың жасалған жиынын қайтарады.

        Args:
            text (str): Қорытындылау үшін мәтін.
            model (str): (Optional) моделдің идентификаторы.
            length (str): (Optional) Қорытындының ұзақтығын басқарады.
                        {"short", "medium", "long"}, әдепкі бойынша "medium".
            format (str): (Optional) Жиынтық форматын басқарады.
                        {"paragraph", "bullets"}, әдепкі бойынша "paragraph".
            extractiveness (str) Түпнұсқа мәтінге қаншалықты жақын екенін басқарады.ү
             {"high", "medium", "low"}.
            temperature (float): 0-ден 5-ке дейінгі диапазондар. Шығудың кездейсоқтығын басқарады.
                 Төменгі мәндер көбірек «болжауға болатын» нәтиже береді, ал жоғары мәндер
                 көбірек «шығармашылық» нәтиже шығаруға бейім. Көбіне нүкте әдетте 0 мен 1 арасында болады.
            additional_command (str): (Optional) Негізгі шақыруға арналған модификатор, міндетті түрде
                 "Generate a summary _" сөйлемді аяқтау. .
        """
        json_body = {
            "model": model,
            "text": text,
            "length": length,
            "format": format,
            "temperature": temperature,
            "additional_command": additional_command,
            "extractiveness": extractiveness,
        }
        # dict ішінен None мәндерін алып тастау
        json_body = {k: v for k, v in json_body.items() if v is not None}
        response = self._request(SUMMARIZE_URL, json=json_body)

        return SummarizeResponse(id=response["id"], summary=response["summary"], meta=response["meta"])

    def _check_response(self, json_response: Dict, headers: Dict, status_code: int):
        if "message" in json_response:  # has errors
            raise APIError(
                message=json_response["message"],
                http_status=status_code,
                headers=headers,
            )
        if 400 <= status_code < 500:
            raise APIError(
                message=f"Unexpected client error (status {status_code}): {json_response}",
                http_status=status_code,
                headers=headers,
            )
        if status_code >= 500:
            raise Error(message=f"Unexpected server error (status {status_code}): {json_response}")

    def _request(self, endpoint, json=None, method="POST", stream=False) -> Any:
        headers = {
            "Authorization": "BEARER {}".format(self.api_key),
            "Content-Type": "application/json",
            "Request-Source": self.request_source,
        }

        url = f"{self.api_url}/{self.api_version}/{endpoint}"
        with requests.Session() as session:
            retries = Retry(
                total=self.max_retries,
                backoff_factor=0.5,
                allowed_methods=["POST", "GET"],
                status_forcelist=RETRY_STATUS_CODES,
                raise_on_status=False,
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))
            session.mount("http://", HTTPAdapter(max_retries=retries))

            if stream:
                return session.request(method, url, headers=headers, json=json, **self.request_dict, stream=True)

            try:
                response = session.request(
                    method, url, headers=headers, json=json, timeout=self.timeout, **self.request_dict
                )
            except requests.exceptions.ConnectionError as e:
                raise ConnectionError(str(e)) from e
            except requests.exceptions.RequestException as e:
                raise Error(f"Unexpected exception ({e.__class__.__name__}): {e}") from e

            try:
                json_response = response.json()
            except jsonlib.decoder.JSONDecodeError:
                raise APIError.from_response(response, message=f"Failed to decode json body: {response.text}")

            self._check_response(json_response, response.headers, response.status_code)
        return json_response
