"""Test suite for phlsys_textconvert."""


import string
import unittest

import phlsys_textconvert


class Test(unittest.TestCase):

    def _check_unicode_to_ascii(self, src, dst):
        value = phlsys_textconvert.lossy_unicode_to_ascii(src)
        self.assertEqual(value, dst)
        self.assertIsInstance(value, type(dst))

    def test_empty(self):
        self._check_unicode_to_ascii("", b"")

    def test_ascii_printable(self):
        self._check_unicode_to_ascii(
            str(string.printable),
            bytes(string.printable, 'ascii'))

    def test_trailing_leading_space(self):
        self._check_unicode_to_ascii("trailing  ", b"trailing  ")
        self._check_unicode_to_ascii("  leading", b"  leading")
        self._check_unicode_to_ascii("trailing\t\t", b"trailing\t\t")
        self._check_unicode_to_ascii("\t\tleading", b"\t\tleading")

    def test_newlines(self):
        self._check_unicode_to_ascii("new\nline", b"new\nline")
        self._check_unicode_to_ascii("windows\r\nline", b"windows\r\nline")
        self._check_unicode_to_ascii("\nline", b"\nline")
        self._check_unicode_to_ascii("\r\nline", b"\r\nline")
        self._check_unicode_to_ascii("new\n", b"new\n")
        self._check_unicode_to_ascii("windows\r\n", b"windows\r\n")

    def test_nuls(self):
        self._check_unicode_to_ascii("nul\0middle", b"nul\0middle")
        self._check_unicode_to_ascii("nul-end\0", b"nul-end\0")
        self._check_unicode_to_ascii("\0nul-start", b"\0nul-start")

    def test_ellipses(self):
        self._check_unicode_to_ascii("time passed\u2026", b"time passed...")

    def test_hyphenation_point(self):
        self._check_unicode_to_ascii("hy\u2027phen\u2027ate", b"hy?phen?ate")

    def test_dashes(self):
        self._check_unicode_to_ascii("\u2010", b"-")
        self._check_unicode_to_ascii("\u2011", b"-")
        self._check_unicode_to_ascii("\u2013", b"-")
        self._check_unicode_to_ascii("\u2013", b"-")
        self._check_unicode_to_ascii("\u2014", b"-")
        self._check_unicode_to_ascii("\u2015", b"-")
        self._check_unicode_to_ascii("\u2212", b"-")

    def test_quotes(self):
        self._check_unicode_to_ascii("\u00b4", b"'")
        self._check_unicode_to_ascii("\u2018", b"'")
        self._check_unicode_to_ascii("\u2019", b"'")
        self._check_unicode_to_ascii("\u201c", b'"')
        self._check_unicode_to_ascii("\u201d", b'"')

    def test_bullets(self):
        self._check_unicode_to_ascii("\u00b7", b"*")
        self._check_unicode_to_ascii("\u2022", b"*")
        self._check_unicode_to_ascii("\u2023", b">")
        self._check_unicode_to_ascii("\u2024", b"*")
        self._check_unicode_to_ascii("\u2043", b"-")
        self._check_unicode_to_ascii("\u25b8", b">")
        self._check_unicode_to_ascii("\u25e6", b"o")

    def test_A_Breathing(self):

        # test we can convert unicode to unicode
        phlsys_textconvert.to_unicode(str('hello'))

        # test we can convert bytes to unicode
        self.assertIsInstance(
            phlsys_textconvert.to_unicode(b'hello'),
            str)

        # test invalid characters get replaced by the replacement character
        self.assertEqual(
            phlsys_textconvert.to_unicode(b'\xFF'),
            '\uFFFD')

        # test 'horizontal ellipses' as UTF8 get replaced
        self.assertEqual(
            phlsys_textconvert.to_unicode(b'\xe2\x80\xa6'),
            '\uFFFD\uFFFD\uFFFD')

        # test we can convert ascii to ascii
        phlsys_textconvert.ensure_ascii(b'hello')

        # test bytes stays bytes
        self.assertIsInstance(
            phlsys_textconvert.ensure_ascii(b'hello'),
            bytes)

        # test invalid characters get replaced by '?'
        self.assertEqual(
            phlsys_textconvert.ensure_ascii(b'\xFF'),
            b'?')

        # test 'horizontal ellipses' as UTF8 get replaced
        self.assertEqual(
            phlsys_textconvert.ensure_ascii(b'\xe2\x80\xa6'),
            b'???')


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
