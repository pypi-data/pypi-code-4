import importlib
import glob
import os
import logging

def load_all_codecs():
    # Loading all codecs in this folder
    for module in glob.glob(os.path.join(os.path.dirname(__file__), "*.py")):
        module = os.path.basename(module)
        if not module.startswith("_") and module != "utils.py" \
            and module != "base_codec.py":
            logging.info("utils.py(codec_interface): Loading \"{}\"".format(module))
            importlib.import_module("."+module[:-3], "batman.codec_interface")

