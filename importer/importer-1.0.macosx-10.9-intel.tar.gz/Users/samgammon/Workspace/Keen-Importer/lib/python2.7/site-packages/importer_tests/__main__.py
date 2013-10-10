# -*- coding: utf-8 -*-

# pragma: nocover

"""

    importer: testrunner
    ~~~~~~~~~~~~~~~~~~~~

    this file collects and runs ``importer``'s testsuite.

"""

# testrunner
import runner


## Run the testsuite! :)
runner.fix_path()  # fix sys.path
runner.run(runner.load())
