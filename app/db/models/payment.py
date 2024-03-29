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


from peewee import BooleanField, CharField, ForeignKeyField, PrimaryKeyField, FloatField

from .promocode import Promocode
from .account_service import AccountService
from .service_cost import ServiceCost
from .payment_method import PaymentMethod
from .payment_method_currency import PaymentMethodCurrency
from .base import BaseModel


class Payment(BaseModel):
    id = PrimaryKeyField()
    account_service = ForeignKeyField(model=AccountService)
    service_cost = ForeignKeyField(model=ServiceCost)
    cost = FloatField()
    payment_method = ForeignKeyField(model=PaymentMethod)
    payment_method_currency = ForeignKeyField(model=PaymentMethodCurrency)
    state = CharField(max_length=64)
    promocode = ForeignKeyField(model=Promocode, null=True, default=None)
    data = CharField(max_length=1024, default='{}', null=True)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'payments'
