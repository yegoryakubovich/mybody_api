#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models.action import Action
from app.db.models.action_parameter import ActionParameter
from app.db.models.language import Language
from app.db.models.text import Text
from app.db.models.text_translate import TextTranslate
from app.db.models.text_pack import TextPack
from app.db.models.icons import Icon
from app.db.models.country import Country
from app.db.models.timezone import Timezone
from app.db.models.currency import Currency
from app.db.models.account import Account
from app.db.models.session import Session


models = (
    Action,
    ActionParameter,
    Language,
    Text,
    TextTranslate,
    TextPack,
    Icon,
    Country,
    Timezone,
    Currency,
    Account,
    Session,
)
