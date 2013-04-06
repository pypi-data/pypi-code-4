from dexy.common import OrderedDict
import dexy.exceptions
import dexy.filter
import dexy.node
import os
import posixpath
import shutil
import stat
import time

class Doc(dexy.node.Node):
    """
    Node representing a single doc.
    """
    aliases = ['doc']
    _settings = {
            'shortcut' : ( """A way to refer to this document without having to
            use the full document key.""", None ),
            'canonical-name' : ("""What the final output name (including path)
                of this document should be.""", None),
            'title' : ("""Title for this document.""", None),
            'output' : ("""Whether to output this document to reports such as
                output/ and output-site/.""", None)
            }

    def setup(self):
        self.name = self.key.split("|")[0]
        self.ext = os.path.splitext(self.name)[1]
        self.filter_aliases = self.key.split("|")[1:]
        self.filters = []
        self.setup_initial_data()

        for alias in self.filter_aliases:
            f = dexy.filter.Filter.create_instance(alias, self)
            self.filters.append(f)

        prev_filter = None
        for i, f in enumerate(self.filters):
            filter_aliases = self.filter_aliases[0:i+1]
            filter_key = "%s|%s" % (self.name, "|".join(filter_aliases))
            storage_key = "%s-%03d-%s" % (self.hashid, i+1, "-".join(filter_aliases))

            if i < len(self.filters) - 1:
                next_filter = self.filters[i+1]
            else:
                next_filter = None

            filter_settings_from_args = self.args.get(f.alias, {})
            f.setup(filter_key, storage_key, prev_filter,
                    next_filter, filter_settings_from_args)
            prev_filter = f

    def setup_datas(self):
        """
        Convenience function to ensure all datas are set up. Should not need to be called normally.
        """
        for d in self.datas():
            if d.state == 'new':
                d.setup()

    def setup_initial_data(self):
        self.canonical_name = self.calculate_canonical_name() or self.name
        storage_key = "%s-000" % self.hashid

        if self.setting('output') is not None:
            canonical_output = self.setting('output')
        else:
            canonical_output = len(self.filter_aliases) == 0

        self.initial_data = dexy.data.Data.create_instance(
                self.data_class_alias(),
                self.name,
                self.ext,
                self.canonical_name,
                storage_key,
                self.setting_values(),
                None,
                canonical_output,
                self.wrapper
                )

    def calculate_canonical_name(self):
        raw_arg_name = self.setting('canonical-name')
    
        if raw_arg_name:
            raw_arg_name = raw_arg_name % self.args

            if "/" in raw_arg_name:
                return raw_arg_name
            else:
                return posixpath.join(posixpath.dirname(self.key), raw_arg_name)

    def consolidate_cache_files(self):
        for node in self.input_nodes():
            node.consolidate_cache_files()

        if self.state == 'cached':
            self.setup_datas()

            # move cache files to new cache
            for d in self.datas():
                if os.path.exists(d.storage.last_data_file()):
                    shutil.move(d.storage.last_data_file(), d.storage.data_file())
                    self.log_debug("Moving %s from %s to %s" % (d.key, d.storage.last_data_file(), d.storage.data_file()))

            if os.path.exists(self.runtime_info_filename(False)):
                shutil.move(self.runtime_info_filename(False), self.runtime_info_filename(True))

            self.apply_runtime_info()
            self.transition('consolidated')

    def apply_runtime_info(self):
            runtime_info = self.load_runtime_info()
            if runtime_info:
                self.add_runtime_args(runtime_info['runtime-args'])
                self.load_additional_docs(runtime_info['additional-docs'])

    def datas(self):
        """
        Returns all associated `data` objects.
        """
        return [self.initial_data] + [f.output_data for f in self.filters]

    def update_all_args(self, new_args):
        for f in self.filters:
            f.input_data.args.update(new_args)
            f.output_data.args.update(new_args)
            f.update_settings(new_args)

    def check_cache_elements_present(self):
        """
        Returns a boolean to indicate whether all files are present in cache.
        """
        # Take this opportunity to ensure Data objects are in `setup` state.
        for d in self.datas():
            if d.state == 'new':
                d.setup()

        return all(
                os.path.exists(d.storage.last_data_file()) or
                os.path.exists(d.storage.this_data_file())
                for d in self.datas())

    def check_doc_changed(self):
        if self.name in self.wrapper.filemap:
            live_stat = self.wrapper.filemap[self.name]['stat']

            self.initial_data.setup()

            in_this_cache = os.path.exists(self.initial_data.storage.this_data_file())
            in_last_cache = os.path.exists(self.initial_data.storage.last_data_file())

            if in_this_cache or in_last_cache:
                # we have a file in the cache from a previous run, compare its
                # mtime to filemap to determine whether it has changed
                if in_this_cache:
                    cache_stat = os.stat(self.initial_data.storage.this_data_file())
                else:
                    cache_stat = os.stat(self.initial_data.storage.last_data_file())

                cache_mtime = cache_stat[stat.ST_MTIME]
                live_mtime = live_stat[stat.ST_MTIME]
                msg = "    cache mtime %s live mtime %s now %s changed (live gt cache) %s"
                msgargs = (cache_mtime, live_mtime, time.time(), live_mtime > cache_mtime)
                self.log_debug(msg % msgargs)
                return live_mtime > cache_mtime
            else:
                # there is no file in the cache, therefore it has 'changed'
                return True
        else:
            # TODO check hash of contents of virtual files
            return False

    def data_class_alias(self):
        data_class_alias = self.args.get('data-class-alias')

        if data_class_alias:
            return data_class_alias
        else:
            contents = self.get_contents()
            if isinstance(contents, OrderedDict):
                return 'sectioned'
            elif isinstance(contents, dict):
                return 'keyvalue'
            else:
                return 'generic'

    def get_contents(self):
        contents = self.args.get('contents')
        return contents

    # Runtime Info
    def runtime_info_filename(self, this=True):
        name = "%s.runtimeargs.pickle" % self.hashid
        return os.path.join(self.initial_data.storage.storage_dir(this), name)

    def save_runtime_info(self):
        """
        Save runtime changes to metadata so they can be reapplied when node has
        been cached.
        """

        info = {
            'runtime-args' : self.runtime_args,
            'additional-docs' : self.additional_doc_info()
            }

        with open(self.runtime_info_filename(), 'wb') as f:
            pickle = self.wrapper.pickle_lib()
            pickle.dump(info, f)

    def load_runtime_info(self):
        info = None

        # Load from 'this' first
        try:
            with open(self.runtime_info_filename(), 'rb') as f:
                pickle = self.wrapper.pickle_lib()
                info = pickle.load(f)
        except IOError:
            pass

        # Load from 'last' if there's nothing in 'this'
        if not info:
            try:
                with open(self.runtime_info_filename(False), 'rb') as f:
                    pickle = self.wrapper.pickle_lib()
                    info = pickle.load(f)
            except IOError:
                pass

        return info

    def run(self):
        self.start_time = time.time()

        if self.name in self.wrapper.filemap:
            # This is a real file on the file system.
            if self.doc_changed or not self.initial_data.is_cached():
                self.initial_data.copy_from_file(self.name)
        else:
            is_dummy = self.initial_data.is_cached() and self.get_contents() == 'dummy contents'
            if is_dummy:
                self.initial_data.load_data()
            else:
                self.initial_data.set_data(self.get_contents())

        for f in self.filters:
            if f.output_data.state == 'new':
                f.output_data.setup()
            f.process()

        self.finish_time = time.time()
        self.elapsed_time = self.finish_time - self.start_time
        self.wrapper.batch.add_doc(self)
        self.save_runtime_info()

        # Run additional docs
        for doc in self.additional_docs:
            doc.check_is_cached()
            for task in doc:
                task()

    def output_data(self):
        """
        Returns a reference to the final data object for this document.
        """
        if self.filters:
            return self.filters[-1].output_data
        else:
            return self.initial_data

    def batch_info(self):
        return {
                'title' : self.output_data().title(),
                'input-data' : self.initial_data.args_to_data_init(),
                'output-data' : self.output_data().args_to_data_init(),
                'filters-data' : [f.output_data.args_to_data_init() for f in self.filters],
                'start_time' : self.start_time,
                'finish_time' : self.finish_time,
                'elapsed' : self.elapsed_time
                }
