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


from .base import ApiException


class WrongPassword(ApiException):
    code = 2000
    message = 'Wrong password'


class AccountUsernameExist(ApiException):
    code = 2001
    message = 'Account with username "{username}" already exist'


class AccountMissingPermission(ApiException):
    code = 2002
    message = 'Account has no "{id_str}" permission'


class InvalidAccountServiceAnswerList(ApiException):
    code = 2003
    message = 'Invalid answer list'