# Copyright (C) 2012 Vaadin Ltd. 
# Copyright (C) 2012 Richard Lincoln
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

"""String validator for e-mail addresses."""

from muntjac.data.validators.regexp_validator import RegexpValidator


class EmailValidator(RegexpValidator):
    """String validator for e-mail addresses. The e-mail address syntax is not
    complete according to RFC 822 but handles the vast majority of valid e-mail
    addresses correctly.

    See L{AbstractStringValidator} for more information.

    @author: Vaadin Ltd.
    @author: Richard Lincoln
    @version: 1.1.2
    """

    def __init__(self, errorMessage):
        """Creates a validator for checking that a string is a syntactically
        valid e-mail address.

        @param errorMessage:
                   the message to display in case the value does not validate.
        """
        super(EmailValidator, self).__init__(('^([a-zA-Z0-9_\\.\\-+])+'
            '@(([a-zA-Z0-9-])+\\.)+([a-zA-Z0-9]{2,4})+$'), True, errorMessage)
