import os
from paste.script import pluginlib
from paste.script.pluginlib import egg_name
from paste.script import create_distro
from paste.script import copydir

def egg_info_dir(base_dir, dist_name):
    all = []
    for dir_extension in ['.'] + os.listdir(base_dir):
        full = os.path.join(base_dir, dir_extension,
                            egg_name(dist_name)+'.egg-info')
        all.append(full)
        if os.path.exists(full):
            return full
    return ''

pluginlib.egg_info_dir = egg_info_dir

def command(self):
    if self.options.list_templates:
        return self.list_templates()
    asked_tmpls = self.options.templates or ['basic_package']
    templates = []
    for tmpl_name in asked_tmpls:
        self.extend_templates(templates, tmpl_name)
    if self.options.list_variables:
        return self.list_variables(templates)
    if self.verbose:
        print 'Selected and implied templates:'
        max_tmpl_name = max([len(tmpl_name) for tmpl_name, tmpl in templates])
        for tmpl_name, tmpl in templates:
            print '  %s%s  %s' % (
                tmpl_name, ' '*(max_tmpl_name-len(tmpl_name)),
                tmpl.summary)
        print
    if not self.args:
        if self.interactive:
            dist_name = self.challenge('Enter project name')
        else:
            raise BadCommand('You must provide a PACKAGE_NAME')
    else:
        dist_name = self.args[0].lstrip(os.path.sep)

    templates = [tmpl for name, tmpl in templates]
    output_dir = os.path.join(self.options.output_dir, dist_name)
    
    pkg_name = self._bad_chars_re.sub('', dist_name.lower())
    vars = {'project': dist_name,
            'package': pkg_name,
            'egg': pluginlib.egg_name(dist_name),
            }
    vars.update(self.parse_vars(self.args[1:]))
    if self.options.config and os.path.exists(self.options.config):
        for key, value in self.read_vars(self.options.config).items():
            vars.setdefault(key, value)
    
    if self.verbose: # @@: > 1?
        self.display_vars(vars)

    if self.options.inspect_files:
        self.inspect_files(
            output_dir, templates, vars)
        return
    if not os.path.exists(output_dir):
        # We want to avoid asking questions in copydir if the path
        # doesn't exist yet
        copydir.all_answer = 'y'
    
    if self.options.svn_repository:
        self.setup_svn_repository(output_dir, dist_name)

    # First we want to make sure all the templates get a chance to
    # set their variables, all at once, with the most specialized
    # template going first (the last template is the most
    # specialized)...
    for template in templates[::-1]:
        vars = template.check_vars(vars, self)

    # Gather all the templates egg_plugins into one var
    egg_plugins = set()
    for template in templates:
        egg_plugins.update(template.egg_plugins)
    egg_plugins = list(egg_plugins)
    egg_plugins.sort()
    vars['egg_plugins'] = egg_plugins
        
    for template in templates:
        self.create_template(
            template, output_dir, vars)

    found_setup_py = False
    paster_plugins_mtime = None

    package_dir = vars.get('package_dir', None)
    if package_dir:
        output_dir = os.path.join(output_dir, package_dir)

    # With no setup.py this doesn't make sense:
    if found_setup_py:
        # Only write paster_plugins.txt if it wasn't written by
        # egg_info (the correct way). leaving us to do it is
        # deprecated and you'll get warned
        egg_info_dir = pluginlib.egg_info_dir(output_dir, dist_name)
        plugins_path = os.path.join(egg_info_dir, 'paster_plugins.txt')
        if len(egg_plugins) and (not os.path.exists(plugins_path) or \
                os.path.getmtime(plugins_path) == paster_plugins_mtime):
            if self.verbose:
                print >> sys.stderr, \
                    ('Manually creating paster_plugins.txt (deprecated! '
                     'pass a paster_plugins keyword to setup() instead)')
            for plugin in egg_plugins:
                if self.verbose:
                    print 'Adding %s to paster_plugins.txt' % plugin
                if not self.simulate:
                    pluginlib.add_plugin(egg_info_dir, plugin)
    
    if self.options.svn_repository:
        self.add_svn_repository(vars, output_dir)

    if self.options.config:
        write_vars = vars.copy()
        del write_vars['project']
        del write_vars['package']
        self.write_vars(self.options.config, write_vars)
 
create_distro.CreateDistroCommand.command = command
