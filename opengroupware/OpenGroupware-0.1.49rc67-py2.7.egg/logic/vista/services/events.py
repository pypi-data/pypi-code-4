#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
VISTA_VECTOR_REFRESHED = 200  # Payload: object_id,
VISTA_VECTOR_CURRENT = 210  # Payload: object_id,
VISTA_VECTOR_ERROR_UNICODE = 220  # Payload: object_id, entity_name, error_text,
VISTA_VECTOR_ERROR_ACCESS = 221  # Payload: object_id, entity_name, error_text,
VISTA_VECTOR_ERROR_OTHER = 222  # Payload: object_id, entity_name, error_text,
VISTA_VECTOR_ERROR_INTEGRITY = 223  # Payload: object_id, entity_name, error_text,
VISTA_INVALID_ENTITY = 230  # Payload: object_id,
VISTA_MISSING_ENTITY = 232  # Payload: object_id
VISTA_UNSUPPORTED_ENTITY = 235  # Payload: object_id, entity_name
VISTA_INDEX_REQUEST = 240  # Payload: object_id
VISTA_INDEX_EXPUNGE = 241  # Payload: object_id
