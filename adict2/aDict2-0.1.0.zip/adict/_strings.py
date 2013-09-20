# aDict — simple dictionary handling
#
# Authors:
#     arseniiv <arseniiv@gmail.com>
#
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

"""_strings.py — aDict format-specific string constants
"""

inline_whitespace = " \t\r\n"
inline_comment_start = "--"
section_brackets = ("[", "]")
signature_section_name = "adict.1"
properties_section_name = "properties"
name_value_separator = "="
articles_section_name = "articles"
homonym_separator = "*"
special_word_marker = "#"
transcription_brackets = ("[", "]")
etymology_marker = "<"
link_marker = ">"
form_link_marker = "="
meaning_marker = "*"
example_marker = ":"
idiom_marker = "~"
translation_marker = "="
rem_brackets = ("((", "))")
em_brackets = ("''", "''")
format_re = r"((?:(?:|\(|')[^('#])+)|#(.*?)#|\(\((.*?)\)\)|''(.*?)''"
