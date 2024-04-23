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


from .accounts import router as router_accounts
from .articles import router as router_articles
from .requests import router as router_requests
from .payments import router as router_payments
from .countries import router as router_countries
from .currencies import router as router_currencies
from .exercises import router as router_exercises
from .images import router as router_images
from .languages import router as router_languages
from .meals import router as router_meals
from .products import router as router_products
from .services import router as router_services
from .sessions import router as router_sessions
from .texts import router as router_texts
from .timezones import router as router_timezones
from .trainings import router as router_trainings
from .urls import router as router_urls
from .promocodes import router as router_promocodes
from .days import router as router_days
from .docs import router as router_docs
from app.utils import Router


router = Router(
    prefix='',
    routes_included=[
        router_sessions,
        router_docs,
        router_requests,
        router_accounts,
        router_articles,
        router_days,
        router_payments,
        router_promocodes,
        router_countries,
        router_currencies,
        router_exercises,
        router_images,
        router_languages,
        router_meals,
        router_products,
        router_services,
        router_texts,
        router_timezones,
        router_trainings,
        router_urls,
    ],
)
