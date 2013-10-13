from __future__ import absolute_import


def to_records(df):
  """The inverse of `pandas.DataFrame.from_records`

  Parameters
  ----------
  df : DataFrame

  Returns
  -------
  rows : list
      list of dicts, one per row in `df`. Index dropped.
  """
  for _, row in df.iterrows():
    yield dict(row)

