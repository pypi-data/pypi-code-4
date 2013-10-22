"""Provides a class for displaying table data in text form."""

import functools
import sys

from collections import namedtuple


class Table:
    """Displays table data in text form."""

    def __init__(self, columns):
        self.columns = columns
        self.rows = []


    def add_row(self, row):
        """Adds a row to the table."""

        self.rows.append(row)


    def add_rows(self, rows):
        """Adds rows to the table."""

        self.rows.extend(rows)


    def draw(self, title=None, stream=None, spacing=3):
        """Prints the table contents."""

        ColumnTraits = namedtuple("ColumnTraits", ("width", "hide"))

        columns_traits = []
        rows = [ {} for i in range(len(self.rows)) ]

        if stream is None:
            stream = sys.stdout

        if title is not None:
            stream.write(title + "\n\n")

        first_visible = True
        for column_id, column in enumerate(self.columns):
            width = 0

            for row_id, row in enumerate(self.rows):
                cell = str(row[column.id]) if column.id in row else ""
                cell_lines = self.__get_cell_lines(cell, max_width=column.max_width)
                rows[row_id][column.id] = cell_lines

                width = functools.reduce(
                    lambda max_len, line: max(max_len, len(line)),
                    cell_lines, width)

            hide = (column.hide_if_empty and width == 0)
            width = max(width, len(column.name))

            columns_traits.append(ColumnTraits(width, hide))

            if not hide:
                if first_visible:
                    first_visible = False
                else:
                    stream.write(" " * spacing)

                stream.write(column.name.center(width))

        stream.write("\n\n")

        for row_id, row in enumerate(rows):
            row_lines = 0
            for column_id, column in enumerate(self.columns):
                if not columns_traits[column_id].hide:
                    row_lines = max(row_lines, len(rows[row_id][column.id]))

            for line_id in range(row_lines):
                first_visible = True

                for column_id, column in enumerate(self.columns):
                    column_traits = columns_traits[column_id]
                    if column_traits.hide:
                        continue

                    if first_visible:
                        first_visible = False
                    else:
                        stream.write(" " * spacing)

                    cell_lines = row[column.id]
                    cell_line = cell_lines[line_id] if line_id < len(cell_lines) else ""

                    if column.align == Column.ALIGN_LEFT:
                        cell_line = cell_line.ljust(column_traits.width)
                    elif column.align == Column.ALIGN_CENTER:
                        cell_line = cell_line.center(column_traits.width)
                    else:
                        cell_line = cell_line.rjust(column_traits.width)

                    stream.write(cell_line)

                stream.write("\n")


    def __get_cell_lines(self, cell, max_width=None):
        """Formats a cell according to column requirements."""

        lines = []

        for source_line in cell.split("\n"):
            line = ""

            for word in source_line.split(" "):
                if (
                    max_width is not None and line and
                    len(line) + 1 + len(word) > max_width
                ):
                    lines.append(line)
                    line = ""

                if line:
                    line += " "
                line += word

            lines.append(line)

        return lines



class Column:
    """Describes a table column."""

    ALIGN_LEFT = "left"
    ALIGN_CENTER = "center"
    ALIGN_RIGHT = "right"

    def __init__(self, id, name, align=ALIGN_RIGHT, max_width=None, hide_if_empty=False):
        self.id = id
        self.name = name
        self.align = align
        self.max_width = max_width
        self.hide_if_empty = hide_if_empty
