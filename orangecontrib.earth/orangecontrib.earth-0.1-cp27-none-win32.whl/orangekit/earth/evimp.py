"""
"""
from collections import defaultdict

import numpy

import Orange
from Orange.ensemble import bagging
from Orange.feature import scoring

from .earth import EarthLearner, EarthClassifier
from .core import subset_selection_xtx

__all__ = ["evimp", "bagged_evimp", "plot_evimp", "ScoreEarthImportance"]


def evimp(model, used_only=True):
    """
    Return the estimated variable importance for the model.

    Parameters
    ----------
    model : Earth
        Earth model.

    """
    if model.subsets is None:
        raise ValueError("No subsets. Use the learner with 'prune=True'.")

    subsets = model.subsets
    n_subsets = numpy.sum(model.best_set)

    rss = -numpy.diff(model.rss_per_subset)
    gcv = -numpy.diff(model.gcv_per_subset)
    attributes = list(model.domain.variables)

    attr2ind = dict(zip(attributes, range(len(attributes))))
    importances = numpy.zeros((len(attributes), 4))
    importances[:, 0] = range(len(attributes))

    for i in range(1, n_subsets):
        term_subset = subsets[i, :i + 1]
        used_attributes = reduce(set.union, [model.used_attributes(term) \
                                             for term in term_subset], set())
        for attr in used_attributes:
            importances[attr2ind[attr]][1] += 1.0
            importances[attr2ind[attr]][2] += gcv[i - 1]
            importances[attr2ind[attr]][3] += rss[i - 1]
    imp_min = numpy.min(importances[:, [2, 3]], axis=0)
    imp_max = numpy.max(importances[:, [2, 3]], axis=0)

    # Normalize importances.
    importances[:, [2, 3]] = 100.0 * (importances[:, [2, 3]] \
                            - [imp_min]) / ([imp_max - imp_min])

    importances = list(importances)
    # Sort by n_subsets and gcv.
    importances = sorted(importances, key=lambda row: (row[1], row[2]),
                         reverse=True)
    importances = numpy.array(importances)

    if used_only:
        importances = importances[importances[:, 1] > 0.0]

    res = [(attributes[int(row[0])], tuple(row[1:])) for row in importances]
    return res


def bagged_evimp(classifier, used_only=True):
    """
    Extract combined (average) :func:`evimp` from an instance of
    :class:`~Orange.ensemble.bagging.BaggedClassifier` using
    :class:`EarthLearner` as a `base_learner`.

    Example::

        from Orange.ensemble.bagging import BaggedLearner
        bc = BaggedLearner(EarthLearner(degree=3, terms=10), data)
        bagged_evimp(bc)

    .. seealso:: :class:`ScoreEarthImportance`

    """
    def assert_type(obj, class_):
        if not isinstance(obj, class_):
            raise TypeError("Instance of %r expected." % (class_))

    assert_type(classifier, bagging.BaggedClassifier)
    bagged_imp = defaultdict(list)
    attrs_by_name = defaultdict(list)
    for c in classifier.classifiers:
        assert_type(c, EarthClassifier)
        imp = evimp(c, used_only=used_only)
        for attr, score in imp:
            bagged_imp[attr.name].append(score)  # map by name
            attrs_by_name[attr.name].append(attr)

    for attr, scores in bagged_imp.items():
        scores = numpy.average(scores, axis=0)
        bagged_imp[attr] = tuple(scores)

    bagged_imp = sorted(bagged_imp.items(),
                        key=lambda t: (t[1][0], t[1][1]),
                        reverse=True)

    bagged_imp = [(attrs_by_name[name][0], scores)
                  for name, scores in bagged_imp]

    if used_only:
        bagged_imp = [(a, r) for a, r in bagged_imp if r[0] > 0]
    return bagged_imp


def plot_evimp(evimp):
    """
    Plot the variable importances as returned from
    :func:`EarthClassifier.evimp`.

    ::

        import Orange, orangekit.earth
        data = Orange.data.Table("housing")
        c = orangekit.earth.EarthLearner(data, degree=3)
        orangekit.earth.plot_evimp(c.evimp())

    .. image:: images/earth-evimp.png

    The left axis is the nsubsets measure and on the right are the normalized
    RSS and GCV.

    """
    import pylab

    if isinstance(evimp, EarthClassifier):
        evimp = evimp.evimp()
    elif isinstance(evimp, bagging.BaggedClassifier):
        evimp = bagged_evimp(evimp)

    fig = pylab.figure()
    axes1 = fig.add_subplot(111)
    attrs = [a for a, _ in evimp]
    imp = [s for _, s in evimp]
    imp = numpy.array(imp)
    X = range(len(attrs))
    l1 = axes1.plot(X, imp[:, 0], "b-", label="nsubsets")
    axes2 = axes1.twinx()

    l2 = axes2.plot(X, imp[:, 1], "g-", label="gcv")
    l3 = axes2.plot(X, imp[:, 2], "r-", label="rss")

    x_axis = axes1.xaxis
    x_axis.set_ticks(X)
    x_axis.set_ticklabels([a.name for a in attrs], rotation=90)

    axes1.yaxis.set_label_text("nsubsets")
    axes2.yaxis.set_label_text("normalized gcv or rss")

    axes1.legend((l1[0], l2[0], l3[0]), ("nsubsets", "gcv", "rss"))

    axes1.set_title("Variable importance")
    fig.show()


#########################################################
# High level interface for measuring variable importance
# (compatible with Orange.feature.scoring module).
#########################################################

def collect_source(variables):
    """
    Given a list of variables ``variables``, return a mapping from source
    variables (``source_variable`` or ``get_value_from.variable`` members)
    back to the variables in ``variables`` (assumes the default preprocessor
    in EarthLearner).

    """
    source = defaultdict(list)
    for var in variables:
        if var.source_variable:
            source[var.source_variable].append(var)
        elif isinstance(var.get_value_from, Orange.core.ClassifierFromVar):
            source[var.get_value_from.variable].append(var)
        elif isinstance(var.get_value_from, Orange.core.ImputeClassifier):
            source[var.get_value_from.classifier_from_var.variable].append(var)
        else:
            source[var].append(var)
    return dict(source)


class ScoreEarthImportance(scoring.Score):
    """
    A subclass of :class:`Orange.feature.scoring.Score` that scores
    features based on their importance in the Earth model using
    ``bagged_evimp``.

    :param int t:
        Number of earth models to train on the data.

    :param int degree:
        The maximum degree of the induced models.

    :param int terms:
        Maximum number of terms induced in the forward pass.

    :param int score_what:
        What to return as a score. Can be one of:

        * ``"nsubsets"``
        * ``"rss"``
        * ``"gcv"``

        string or or class constants:

        * ``NSUBSETS``
        * ``RSS``
        * ``GCV``

    """
    # Return types

    #: The number of subsets the feature is included during the
    #: pruning pass.
    NSUBSETS = 0

    #: Residual squared error increase when the feature was removed
    #: during the pruning pass (averaged over all `t` models)
    RSS = 1

    #: GCV increase when the feature was removed during the pruning pass
    #: (averaged over all `t` models)
    GCV = 2

    handles_discrete = True
    handles_continuous = True
    computes_thresholds = False
    needs = scoring.Score.Generator

    def __new__(cls, attr=None, data=None, weight_id=None, **kwargs):
        self = scoring.Score.__new__(cls)
        if attr is not None and data is not None:
            self.__init__(**kwargs)
            # TODO: Should raise a warning, about caching
            return self.__call__(attr, data, weight_id)
        elif not attr and not data:
            return self
        else:
            raise ValueError("Both 'attr' and 'data' arguments expected.")

    def __init__(self, t=10, degree=2, terms=10, score_what="nsubsets",
                 cached=True):
        self.t = t
        self.degree = degree
        self.terms = terms
        if isinstance(score_what, basestring):
            score_what = {"nsubsets": self.NSUBSETS, "rss": self.RSS,
                          "gcv": self.GCV}.get(score_what, None)

        if score_what not in range(3):
            raise ValueError("Invalid  'score_what' parameter.")

        self.score_what = score_what
        self.cached = cached
        self._cache_ref = None
        self._cached_evimp = None

    def __call__(self, attr, data, weight_id=None):
        """
        Return the score for `attr` as evaluated on `data`.

        :param Orange.feature.Descriptor attr:
            A feature descriptor present in ``data.domain.features``.

        :param Orange.data.Table data:
            Model training data.

        .. note:: `weight_id` is ignored.

        """
        ref = self._cache_ref
        if ref is not None and ref is data:
            evimp = self._cached_evimp
        else:
            learner = bagging.BaggedLearner(
                EarthLearner(degree=self.degree, terms=self.terms),
                t=self.t
            )
            bc = learner(data, weight_id)
            evimp = bagged_evimp(bc, used_only=False)
            self._cache_ref = data
            self._cached_evimp = evimp

        evimp = dict(evimp)
        score = evimp.get(attr, None)

        if score is None:
            source = collect_source(evimp.keys())
            if attr in source:
                # Return average of source var scores
                return numpy.average([evimp[v][self.score_what] \
                                      for v in source[attr]])
            else:
                raise ValueError("Attribute %r not in the domain." % attr)
        else:
            return score[self.score_what]


class ScoreRSS(scoring.Score):

    handles_discrete = False
    handles_continuous = True
    computes_thresholds = False

    def __new__(cls, attr=None, data=None, weight_id=None, **kwargs):
        self = scoring.Score.__new__(cls)
        if attr is not None and data is not None:
            self.__init__(**kwargs)
            # TODO: Should raise a warning, about caching
            return self.__call__(attr, data, weight_id)
        elif not attr and not data:
            return self
        else:
            raise ValueError("Both 'attr' and 'data' arguments expected.")

    def __init__(self):
        self._cache_data = None
        self._cache_rss = None

    def __call__(self, attr, data, weight_id=None):
        ref = self._cache_data
        if ref is not None and ref is data:
            rss = self._cache_rss
        else:
            x, y = data.to_numpy_MA("1A/c")
            subsets, rss = subset_selection_xtx(x, y)
            rss_diff = -numpy.diff(rss)
            rss = numpy.zeros_like(rss)
            for s_size in range(1, subsets.shape[0]):
                subset = subsets[s_size, :s_size + 1]
                rss[subset] += rss_diff[s_size - 1]
            rss = rss[1:]  # Drop the intercept
            self._cache_data = data
            self._cache_rss = rss

        index = list(data.domain.attributes).index(attr)
        return rss[index]
