# ==================================================================================================
# Copyright 2013 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

from __future__ import print_function

__author__ = "tdesai"

import os
import pkgutil

from twitter.common.dirutil import safe_mkdir, touch
from twitter.pants import binary_util, get_buildroot
from twitter.pants.base.generator import Generator, TemplateData
from twitter.pants.tasks import TaskError


DEFAULT_CONFS = ['default']
TEMPLATE_PATH = os.path.join('templates', 'ivy_resolve', 'ivy.mk')


#TODO: Try to refactor ivy_resolve.py and use that
#Refer AWESOME-4329
class IvyResolver(object):
  def __init__(self, context, jvm_tool_spec):
    self._config = context.config
    self._jvm_tool_spec = jvm_tool_spec
    self._name = self._jvm_tool_spec.name
    self._dependencies = self._jvm_tool_spec.dependencies

  def make_runnable(self):
    self._workdir = self._config.get(self._name, 'workdir',
                                     default=os.path.join(self._config.getdefault('homedir'),
                                                          '.pants.d',
                                                          self._name))
    safe_mkdir(self._workdir)
    self._confs = self._config.getlist(self._name, 'confs', default=DEFAULT_CONFS)
    ivy_xml = self._generate_ivy_xml()
    self._run_ivy_resolve(ivy_xml)

  def _generate_ivy_xml(self):
    ivy_xml = os.path.join(self._workdir, 'ivy.xml')
    template_data = TemplateData(
        org="com.twitter",
        module=self._name,
        version='',
        publications=None,
        is_idl=False,
        dependencies=[self._generate_jar_template(jar) for jar in self._dependencies],
        excludes=[]
    )
    with open(ivy_xml, 'w') as output:
      generator = Generator(pkgutil.get_data(__name__, TEMPLATE_PATH),
                            lib=template_data)
      generator.write(output)
    return ivy_xml

  def _generate_jar_template(self, jar):
    return TemplateData(org=jar.org,
                        module=jar.name,
                        version=jar.rev,
                        mutable=self._is_mutable(jar),
                        force=jar.force,
                        excludes=[self._generate_exclude_template(exclude)
                                    for exclude in jar.excludes],
                        transitive=jar.transitive,
                        artifacts=jar.artifacts,
                        is_idl='idl' in jar._configurations,
                        configurations=';'.join(jar._configurations))

  def _is_mutable(self, jar):
    if jar.mutable is not None:
      return jar.mutable
            #TODO: setup_parser
            #if self._mutable_pattern:
            #return self._mutable_pattern.match(jar.rev)
    return False

  def _generate_exclude_template(self, exclude):
    return TemplateData(org=exclude.org, name=exclude.name)

  def _run_ivy_resolve(self, ivy_xml, ivy_settings=None):
    #TODO: https://jira.twitter.biz/browse/AWESOME-4330
    tool_libdir = os.path.join(self._workdir, 'lib')
    tool_check = '%s.checked' % tool_libdir
    if not os.path.exists(tool_check):
      safe_mkdir(tool_libdir)
      ivy_settings = ivy_settings or self._config.get('ivy', 'ivy_settings')
      ivy_opts = ['-settings', ivy_settings,
                  '-ivy', ivy_xml,
                  '-cache', self._config.get('ivy-resolve', 'cache_dir'),
                  '-retrieve', '%s/[artifact]-[revision](-[classifier]).[ext]' % tool_libdir,
                  '-confs', ','.join(self._confs)]
      classpath = binary_util.get_tool_classpath(tool_lib_dir=os.path.join(get_buildroot(),
                                                                           'build-support',
                                                                           'ivy',
                                                                           'lib'))
      result = binary_util.runjava_indivisible(main='org.apache.ivy.Main',
                                               classpath=classpath,
                                               opts=ivy_opts)
      if result != 0:
        raise TaskError('Failed to load tool %s, ivy exit code %d' % (self._name, result))
      touch(tool_check)
