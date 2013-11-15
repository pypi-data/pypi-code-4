# Copyright (c) 2013, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of upack nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement


import datetime
import re

import upack.context
import upack.write


__all__ = ('RPMWriter',)


class RPMWriter(upack.write.Writer):

    NAME = 'rpm'

    def __init__(self):
        super(RPMWriter, self).__init__()

    def write(self, ctx, package):
        ctx.push(self.context())
        ctx.push(package)
        pkg = ctx.format(
'''Name:           {name}
Version:        {version}
Release:        {release}{dist}
Summary:        {summary}

License:        {license}
URL:            {homepage}
Source0:        {tarball}

BuildRequires:  {build-requires}
Requires:       {requires}
Conflicts:      {conflicts}

%description
{description}
''')
        for subpackage in package.subpackages:
            ctx.push(subpackage)
            pkg += ctx.format(
'''
%package        -n {name}
Summary:        {summary}
Requires:       {requires}
Conflicts:      {conflicts}
%description    -n {name}
{description}
''')
            ctx.pop()
        pkg += ctx.format(
'''
%prep
%setup -q

%build
%configure {configure}
make %{{?_smp_mflags}}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
''')
        if [x for x in package.files if re.search('\.so(\.[0-9])+', x)]:
            pkg += ctx.format('%post -n {name} -p /sbin/ldconfig\n')
            pkg += ctx.format('%postun -n {name} -p /sbin/ldconfig\n')
        for subpackage in package.subpackages:
            if [x for x in subpackage.files if re.search('\.so(\.[0-9])+', x)]:
                ctx.push(subpackage)
                pkg += ctx.format('%post -n {name} -p /sbin/ldconfig\n')
                pkg += ctx.format('%postun -n {name} -p /sbin/ldconfig\n')
                ctx.pop()
        pkg += ctx.format(
'''
%files
%defattr(-,root,root,-)
''')
        for f in package.files:
            pkg += ctx.format(f) + '\n'
        for f in package.excludes:
            pkg += ctx.format('%exclude ' + f) + '\n'
        for subpackage in package.subpackages:
            ctx.push(subpackage)
            pkg += ctx.format('\n%files          -n {name}\n')
            for f in subpackage.files:
                pkg += ctx.format(f) + '\n'
            ctx.pop()
        pkg += ctx.format(
'''
%changelog

* {date} {user_name} <{user_email}> - {version}-{release}
- Automatically generated using upack
''')
        pkg = '\n'.join([x for x in pkg.split('\n')
                         if not x.strip(' \t').endswith(':')])
        fout = open(package.name + '.spec', 'w')
        fout.write(pkg)
        fout.flush()
        fout.close()
        fout = open('Makefile.rpm.' + package.name, 'w')
        fout.write(ctx.format(
'''all:
	cp {name}.spec ${{HOME}}/rpmbuild/SPECS
	cp {name}-{version}.tar.gz ${{HOME}}/rpmbuild/SOURCES
	rm -f {name} ${{HOME}}/rpmbuild/SRPMS/{name}*
	rpmbuild -bs ${{HOME}}/rpmbuild/SPECS/{name}.spec
	mock -r default ${{HOME}}/rpmbuild/SRPMS/{name}*
'''))
        ctx.pop()
        ctx.pop()

    def context(self):
        r = upack.context.Raw
        d = {}
        d['date'] = datetime.datetime.now().strftime('%a %b %d %Y')
        d['dev'] = 'devel'
        d['dist'] = r('%{?dist}')
        d['self'] = r('%{?_isa} = %{version}-%{release}')
        d['bindir'] = r('%{_bindir}')
        d['includedir'] = r('%{_includedir}')
        d['javadir'] = r('%{_javadir}')
        d['libdir'] = r('%{_libdir}')
        d['libexecdir'] = r('%{_libexecdir}')
        d['mandir'] = r('%{_mandir}')
        d['pythondir'] = r('%{python_sitearch}')
        return d
