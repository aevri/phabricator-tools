"""show the configuration as discovered from the current directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_showconfig
#
# Public Functions:
#   getFromfilePrefixChars
#   setup_parser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setup_parser(parser):
    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    getExplanation = phlsys_makeconduit.get_uri_user_cert_explanation
    uri, user, cert, explanation = getExplanation(
        args.uri, args.user, args.cert)
    print(explanation)
    print()
    print("uri : ", uri)
    print("user: ", user)
    print("cert: ", phlsys_makeconduit.obscured_cert(cert))


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
