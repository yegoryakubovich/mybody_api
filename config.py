#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_port: int
    tasks_flower_port: int

    tg_bot_token: str
    tg_request_chat_id: str
    tg_new_request_message: str
    tg_new_purchase_message: str

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_name: str

    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str

    flower_user: str
    flower_password: str

    root_token: str
    sync_db_url: str
    sync_db_table_name: str

    payment_hg_url: str
    payment_hg_client_id: int
    payment_hg_client_secret: str
    payment_hg_service_provider_id: int
    payment_hg_service_id: int
    payment_hg_service_provider_name: str
    payment_hg_service_name: str
    payment_hg_address_country: str
    payment_hg_address_line: str
    payment_hg_address_city: str
    payment_hg_full_address: str
    payment_hg_locality_code: str
    payment_hg_store_name: str
    payment_hg_store_locality_name: str
    payment_hg_store_city: str
    payment_hg_store_locality_city: str
    payment_hg_prefix: str

    secret_promo_code: str

    path_articles: str = 'assets/articles'
    path_texts_packs: str = 'assets/texts_packs'
    path_images: str = 'assets/images'
    items_per_page: int = 10

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
