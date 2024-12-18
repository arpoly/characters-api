import allure
import requests
from marshmallow import ValidationError
from requests.auth import HTTPBasicAuth

from config import API_BASE_URL, USERNAME, PASSWORD
from src.logger import log_request_response, logger


class BaseHttpClient:
    def __init__(self):
        self.session = requests.Session()

    def handle_response(self, response: requests.Response):
        return log_request_response(response)

    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        try:
            response = self.session.request(method, url, **kwargs)
            self.handle_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {method} {url}: {e}")
            raise

    @allure.step("Валидация тела ответа")
    def validate_response(self, data: dict, schema):
        logger.info("Starting validation of response data.")
        try:
            schema().load(data)
            logger.info("Response data validated successfully.")
        except ValidationError as err:
            logger.error(f"Response validation failed: {err.messages}")
            raise Exception(f"Response validation failed: {err.messages}")


class CharacterClient(BaseHttpClient):
    def __init__(self, api_base_url=None, username=USERNAME, password=PASSWORD, timeout=5):
        super().__init__()
        self.api_base_url = api_base_url or API_BASE_URL
        if not self.api_base_url:
            raise ValueError("API_BASE_URL не задано.")
        self.session.auth = HTTPBasicAuth(username, password)
        self.timeout = timeout

    @allure.step("Получение списка персонажей")
    def get_characters(self) -> requests.Response:
        return self.make_request('GET', f'{self.api_base_url}/characters', timeout=self.timeout)

    @allure.step("Получение персонажа по имени")
    def get_character_by_name(self, name: str) -> requests.Response:
        return self.make_request('GET', f'{self.api_base_url}/character', params={'name': name},
                                 timeout=self.timeout)

    @allure.step("Добавление нового персонажа")
    def add_character(self, character_data: dict) -> requests.Response:
        return self.make_request('POST', f'{self.api_base_url}/character', json=character_data,
                                 timeout=self.timeout)

    @allure.step("Обновление персонажа")
    def update_character(self, character_data: dict) -> requests.Response:
        return self.make_request('PUT', f'{self.api_base_url}/character', json=character_data,
                                 timeout=self.timeout)

    @allure.step("Удаление персонажа")
    def delete_character(self, name: str) -> requests.Response:
        return self.make_request('DELETE', f'{self.api_base_url}/character', params={'name': name},
                                 timeout=self.timeout)
