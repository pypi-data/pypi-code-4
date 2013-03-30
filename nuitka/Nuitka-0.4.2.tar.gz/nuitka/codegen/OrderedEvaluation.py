#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Generate code that enforces ordered evaluation.

"""

def getEvalOrderedCode( context, args ):
    args_length = len( args )

    if args_length > 1:
        context.addEvalOrderUse( args_length )

        return "EVAL_ORDERED_%d( %s )" % (
            args_length,
            ", ".join( args )
        )
    else:
        return ", ".join( args )
