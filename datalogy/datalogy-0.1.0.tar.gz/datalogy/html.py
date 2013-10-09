from pyquery import PyQuery as pq

from datalogy import util


def clean_table(table):
    """Removes empty rows, deletes row duplicates"""
    cleaned_table = []
    for row in table:
        row = strip_unprintables(remove_nbsp(row))
        if row and util.non_empty(row):
            cleaned_table.append(row)

    return cleaned_table


def normalise_tabular_labelling(row, marker_item):
    """Removes duplicate column labels"""
    for item in row:
        if item == marker_item:
            row.remove(item)
    return row


def parse_html_table(html):
    html_table = []
    document = pq(html)
    for row in document('table > tr'):
        row_data = []
        for cell in row.iterchildren():
            row_data.append(cell.text)
        html_table.append(row_data)

    return html_table


def remove_nbsp(row):
    return [cell for cell in row if cell and not cell == '&nbsp;']


def strip_unprintables(row):
    """Strip unprintable unicode characters"""
    printables = []
    for cell in row:
        if isinstance(cell, basestring):
            printables.append(
                unicode(cell).replace(u'\xa0', '')
            )
        else:
            printables.append(cell)
    return printables
