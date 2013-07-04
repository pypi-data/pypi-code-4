# -*- coding: utf-8 -*-

import os
from datetime import datetime
from lxml import etree

from radish.config import Config
from radish.filesystemhelper import FileSystemHelper as fsh


class XunitWriter(object):
    REPORT_FILENAME = "radishtests.xml"
    ONE_XUNIT = "radish.one_xunit"

    def __init__(self, endResult):
        self._endResult = endResult

    def generate(self):
        outputs = {}
        if Config().split_xunit:
            for f in self._endResult.get_features():
                filename = fsh.filename(f.get_filename(), with_extension=False)
                path = os.path.join(Config().xunit_file, filename + ".xml")
                if path not in outputs:
                    outputs[path] = []
                outputs[path].append(f)
        else:
            outputs[XunitWriter.ONE_XUNIT] = self._endResult.get_features()

        for filename, features in outputs.iteritems():
            if filename == XunitWriter.ONE_XUNIT:
                filename = Config().xunit_file or XunitWriter.REPORT_FILENAME

            testsuite = etree.Element(
                "testsuite",
                name="radish",
                hostname="localhost",
                id=unicode(Config().marker),
                time=str(sum([f.get_duration() for f in features])),
                tests=str(self._endResult.get_total_steps()),
                failures=str(self._endResult.get_failed_steps()),
                skipped=str(self._endResult.get_skipped_steps()),
                errors="0",
                timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )

            # append steps to testsuite
            for f in features:
                for s in f.get_scenarios():
                    for step in s.get_steps():
                        testsuite.append(step.get_report_as_xunit_tag())

            with open(filename, "w") as f:
                f.write(etree.tostring(testsuite, pretty_print=True, xml_declaration=True, encoding="utf-8"))
