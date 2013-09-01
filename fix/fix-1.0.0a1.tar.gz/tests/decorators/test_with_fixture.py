"""Tests for the `fix.with_fixture` function."""

from __future__ import with_statement

import os
import shutil
import tempfile

from types import FunctionType

from fix import with_fixture


def test_exists():
    """`fix.with_fixture` function exists"""
    assert isinstance(with_fixture, FunctionType)


def test_setup_only():
    """`setup_only` fixture works as expected"""

    def setup_only(context):
        """A fixture with no `teardown()`."""

        def setup():
            """Add something to the context."""
            assert context == {}
            context.squee = "kapow"

        return setup

    @with_fixture(setup_only)
    def case(context):
        """Check that the context has been set up."""
        assert context == {"squee": "kapow"}

    case()  # pylint: disable=E1120


def test_setup_teardown():
    """`setup_teardown` fixture works as expected"""

    def setup_teardown(context):
        """A fixture with both `setup()` and `teardown()`."""

        def setup():
            """Add something to the context."""
            assert context == {}
            context.squee = "kapow"

        def teardown():
            """Check that `context.squee` has changed."""
            assert context == {"squee": "boing"}

        return setup, teardown

    @with_fixture(setup_teardown)
    def case(context):
        """Alter the context."""
        assert context == {"squee": "kapow"}
        context.squee = "boing"

    case()  # pylint: disable=E1120


def test_multiple_invocation():
    """`multiple` fixture creates a fresh context each invocation"""

    def multiple(context):
        """A fixture to be invoked multiple times."""

        def setup():
            """Add something to the context."""
            assert context == {}
            context.squee = "kapow"

        def teardown():
            """Check that `context.squee` has changed."""
            assert context == {"squee": "kapow", "boing": "thunk"}

        return setup, teardown

    @with_fixture(multiple)
    def case(context):
        """Add to the context."""
        assert context == {"squee": "kapow"}
        context.boing = "thunk"

    for _ in range(3):
        case()  # pylint: disable=E1120


def test_external():
    """`external` fixture interacts as expected with the 'real world'."""

    def external(context, files=3):
        """A fixture to manipulate temporary files and directories."""

        def setup():
            """Create some temporary files."""
            context.temp_dir = tempfile.mkdtemp()
            context.filenames = ["file_%03d" % i for i in range(files)]
            for filename in context.filenames:
                with open(os.path.join(context.temp_dir, filename), "w") as f:
                    f.write("This is the file %r.\n" % filename)

        def teardown():
            """Delete the temporary files created in `setup()`."""
            shutil.rmtree(context.temp_dir)

        return setup, teardown

    @with_fixture(external, files=5)
    def check_files(context):
        """Return the number of present and absent files."""
        present = 0
        absent = 0
        for filename in context.filenames:
            if os.path.exists(os.path.join(context.temp_dir, filename)):
                present += 1
            else:
                absent += 1
        return context.temp_dir, present, absent

    temp_dir, present, absent = check_files()  # pylint: disable=E1120
    assert not os.path.exists(temp_dir)
    assert present == 5
    assert absent == 0
