#Copyright 2013 Sebastian Kreft
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import gitlint


def convert_to_man_page(text):
    text = text.strip()
    lines = text.split('\n')
    sections = []
    sections.append(('NAME', lines[0]))
    section = 'DESCRIPTION'
    content = []
    for line in lines[1:]:
        if line.strip().upper() in ('OPTIONS:', 'USAGE:', 'BUGS:',):
            sections.append((section, '\n'.join(content)))
            section = line.strip().upper().replace(':', '')
            if section == 'USAGE':
                section = 'SYNOPSIS'
            content = []
        else:
            content.append(line)
    sections.append((section, '\n'.join(content)))
    sections[1], sections[2] = sections[2], sections[1]
    man = '.TH GIT-LINT 1 "11/10/2013" "Git-lint v0.1" "Git-Lint Manual"\n'
    for section, content in sections:
        man += '.SH %s\n%s\n' % (section, content)
    return man


if __name__ == '__main__':
    print convert_to_man_page(gitlint.__doc__)
