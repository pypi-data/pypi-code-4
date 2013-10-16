"""
Earth Orange interface

Example::

    >>> import Orange, orangecontrib.earth
    >>> data = Orange.data.Table("housing")
    >>> c = orangecontrib.earth.EarthLearner(data, degree=2, terms=10)
    >>> print c.to_string(precision=2)
    MEDV =
       23.59
       -0.61 * max(0, LSTAT - 6.12)
       +11.90 * max(0, RM - 6.43)
       +1.14 * max(0, 6.43 - RM)
       -228.80 * max(0, NOX - 0.65) * max(0, RM - 6.43)
       +0.02 * max(0, TAX - 307.00) * max(0, 6.12 - LSTAT)
       +0.03 * max(0, 307.00 - TAX) * max(0, 6.12 - LSTAT)

"""

from __future__ import division

__all__ = ["EarthLearner", "EarthClassifier", "evimp", "bagged_evimp",
           "ScoreEarthImportance"]

import numpy

import Orange

from .core import forward_pass, pruning_pass, base_term_transform


def is_discrete(var):
    return isinstance(var, Orange.feature.Discrete)


def is_continuous(var):
    return isinstance(var, Orange.feature.Continuous)


def expand_discrete(var):
    """
    Expand a discrete variable ``var`` returning one continuous indicator
    variable for each value of ``var`` (if the number of values is grater
    then 2 else return only one indicator variable).

    """
    if len(var.values) > 2:
        values = var.values
    elif len(var.values) == 2:
        values = var.values[-1:]
    else:
        values = var.values[:1]
    new_vars = []
    for value in values:
        new = Orange.feature.Continuous("{0}={1}".format(var.name, value))
        new.get_value_from = cls = Orange.core.ClassifierFromVar(whichVar=var)
        cls.transformer = Orange.core.Discrete2Continuous()
        cls.transformer.value = int(Orange.core.Value(var, value))
        new.source_variable = var
        new_vars.append(new)
    return new_vars


def select_attrs(table, features, class_var=None,
                 class_vars=None, metas=None):
    """
    Select only ``features`` from the ``table``.
    """
    if class_vars is None:
        domain = Orange.data.Domain(features, class_var)
    else:
        domain = Orange.data.Domain(features, class_var, class_vars=class_vars)
    if metas:
        domain.add_metas(metas)

    return Orange.data.Table(domain, table)


class EarthLearner(Orange.regression.base.BaseRegressionLearner):
    """
    Earth learner class.

    Supports both regression and classification problems. For classification,
    class values are expanded into continuous indicator columns (one for
    each value if the number of values is grater then 2), and a multi
    response model is fit to these new columns. The resulting classifier
    computes response values on new instances to select the final
    predicted class.

    :param int degree:
        Maximum degree (num. of hinge functions per term) of the terms
        in the model (default: 1).
    :param int terms:
        Maximum number of terms in the forward pass. If set to ``None``
        (default), ``min(200, max(20, 2 * n_attributes)) + 1`` will be
        used, like the default setting in earth R package.
    :param float penalty:
        Penalty for hinges in the GCV computation (used in the pruning pass).
        Default is 3.0 if ``degree`` is above 1, and 2.0 otherwise.
    :param float thresh:
        Threshold for RSS decrease in the forward pass (default: 0.001).
    :param int min_span: TODO.
    :param float new_var_penalty:
        Penalty for introducing a new variable in the model during the
        forward pass (default: 0).
    :param int fast_k: Fast k.
    :param float fast_beta: Fast beta.
    :param int pruned_terms:
        Maximum number of terms in the model after pruning (default:
        ``None``, no limit).
    :param bool scale_resp:
        Scale responses prior to forward pass (default: ``True``);
        Ignored for models with multiple responses.
    :param bool store_instances:
        Store training instances in the model (default: ``True``).

    """

    def __new__(cls, instances=None, weight_id=None, **kwargs):
        self = Orange.regression.base.BaseRegressionLearner.__new__(cls)
        if instances is not None:
            self.__init__(**kwargs)
            return self.__call__(instances, weight_id)
        else:
            return self

    def __init__(self, degree=1, terms=None, penalty=None, thresh=1e-3,
                 min_span=0, new_var_penalty=0, fast_k=20, fast_beta=1,
                 pruned_terms=None, scale_resp=True, store_instances=True,
                **kwds):

        super(EarthLearner, self).__init__()

        self.degree = degree
        self.terms = terms
        if penalty is None:
            penalty = 3 if degree > 1 else 2
        self.penalty = penalty
        self.thresh = thresh
        self.min_span = min_span
        self.new_var_penalty = new_var_penalty
        self.fast_k = fast_k
        self.fast_beta = fast_beta
        self.pruned_terms = pruned_terms
        self.scale_resp = scale_resp
        self.store_instances = store_instances
        self.__dict__.update(kwds)

        self.continuizer.class_treatment = \
            Orange.data.preprocess.DomainContinuizer.Ignore

    def __call__(self, instances, weight_id=None):
        """
        Train an :class:`EarthClassifier` instance on the `instances`.

        :param Orange.data.Table instances: Training instances.

        .. note:: `weight_id` is ignored.

        """
        expanded_class = None
        multitarget = False

        if instances.domain.class_var:
            instances = self.impute_table(instances)
            instances = self.continuize_table(instances)

            if is_discrete(instances.domain.class_var):
                # Expand a discrete class with indicator columns
                expanded_class = expand_discrete(instances.domain.class_var)
                y_table = select_attrs(instances, expanded_class)
                (y, ) = y_table.to_numpy_MA("A")
                (x, ) = instances.to_numpy_MA("A")
            elif is_continuous(instances.domain.class_var):
                x, y, _ = instances.to_numpy_MA()
                y = y.reshape((-1, 1))
            else:
                raise ValueError("Cannot handle the response.")
        elif instances.domain.class_vars:
            # Multi-target domain
            if not all(map(is_continuous, instances.domain.class_vars)):
                raise TypeError("Only continuous multi-target classes are "
                                "supported.")
            x_table = select_attrs(instances, instances.domain.attributes)
            y_table = select_attrs(instances, instances.domain.class_vars)

            # Impute and continuize only the x_table
            x_table = self.impute_table(x_table)
            x_table = self.continuize_table(x_table)

            (x, ) = x_table.to_numpy_MA("A")
            (y, ) = y_table.to_numpy_MA("A")

            multitarget = True
        else:
            raise ValueError("Class variable expected.")

        # check for non-finite values in y.
        if not numpy.isfinite(y).all():
            raise ValueError("Non-finite values present in Y")

        # mask non-finite values in x.
        x = numpy.ma.masked_invalid(x, copy=False)

        if self.scale_resp and y.shape[1] == 1:
            sy = y - numpy.ma.mean(y, axis=0)
            sy = sy / numpy.ma.std(sy, axis=0)
        else:
            sy = y

        # replace masked values with means.
        if numpy.ma.is_masked(sy):
            mean_sy = numpy.ma.mean(sy, axis=0)
            sy = numpy.where(sy.mask, mean_sy, sy)

        if numpy.ma.is_masked(x):
            mean_x = numpy.ma.mean(x, axis=0)
            x = numpy.where(x.mask, mean_x, x)

        terms = self.terms
        if terms is None:
            # Automatic maximum number of terms
            terms = min(200, max(20, 2 * x.shape[1])) + 1

        n_terms, used, bx, dirs, cuts = forward_pass(
            x, sy, degree=self.degree, terms=terms, penalty=self.penalty,
            thresh=self.thresh, min_span=self.min_span,
            fast_k=self.fast_k, fast_beta=self.fast_beta,
            new_var_penalty=self.new_var_penalty
        )

        # discard unused terms from bx, dirs, cuts
        bx = bx[:, used]
        dirs = dirs[used, :]
        cuts = cuts[used, :]

        # pruning
        used, subsets, rss_per_subset, gcv_per_subset = \
            pruning_pass(bx, y, self.penalty,
                         max_pruned_terms=self.pruned_terms)

        # Fit final betas to the selected subset of basis terms.
        bx_used = bx[:, used]
        betas, res, rank, s = numpy.linalg.lstsq(bx_used, y)

        return EarthClassifier(
                   instances.domain, used, dirs, cuts, betas.T,
                   subsets, rss_per_subset, gcv_per_subset,
                   instances=instances if self.store_instances else None,
                   multitarget=multitarget,
                   expanded_class=expanded_class
               )


def soft_max(values):
    values = numpy.asarray(values)
    return numpy.exp(values) / numpy.sum(numpy.exp(values))


class EarthClassifier(Orange.core.ClassifierFD):
    """
    Earth classifier.
    """
    def __init__(self, domain, best_set, dirs, cuts, betas, subsets=None,
                 rss_per_subset=None, gcv_per_subset=None, instances=None,
                 multitarget=False, expanded_class=None,
                 **kwargs):
        self.multitarget = multitarget
        self.domain = domain
        self.class_var = domain.class_var
        if self.multitarget:
            self.class_vars = domain.class_vars

        self.best_set = best_set
        self.dirs = dirs
        self.cuts = cuts
        self.betas = betas
        self.subsets = subsets
        self.rss_per_subset = rss_per_subset
        self.gcv_per_subset = gcv_per_subset
        self.instances = instances
        self.expanded_class = expanded_class
        self.__dict__.update(kwargs)

    def __call__(self, instance, result_type=Orange.core.GetValue):
        """
        Predict the response value on `instance`.

        :param Orange.data.Instance instance:
            Input data instance.

        """
        if self.multitarget and self.domain.class_vars:
            resp_vars = list(self.domain.class_vars)
        elif is_discrete(self.class_var):
            resp_vars = self.expanded_class
        else:
            resp_vars = [self.class_var]

        vals = self.predict(instance)
        vals = [var(val) for var, val in zip(resp_vars, vals)]

        from Orange.statistics.distribution import Distribution

        if not self.multitarget and is_discrete(self.class_var):
            dist = Distribution(self.class_var)

            # Random gen. for tie breaking.
            dist.random_generator = Orange.misc.Random(hash(instance))

            if len(self.class_var.values) == 2:
                probs = [1 - float(vals[0]), float(vals[0])]
            else:
                probs = soft_max(map(float, vals))

            for val, p in zip(self.class_var.values, probs):
                dist[val] = p
            value = dist.modus()
            vals, probs = [value], [dist]
        else:
            probs = []
            for var, val in zip(resp_vars, vals):
                dist = Distribution(var)
                dist[val] = 1.0
                probs.append(dist)

        if not self.multitarget:
            vals, probs = vals[0], probs[0]

        if result_type == Orange.core.GetValue:
            return vals
        elif result_type == Orange.core.GetBoth:
            return vals, probs
        else:
            return probs

    def base_matrix(self, instances=None):
        """
        Return the base matrix (bx) of the Earth model for the table.

        Base matrix is a len(instances) * num_terms matrix of computed values
        of terms in the model (not multiplied by beta) for each instance.

        If table is not supplied, the base matrix of the training instances
        is returned.

        :param Orange.data.Table instances:
            Input instances for the base matrix.

        """
        if instances is None:
            instances = self.instances
        instances = select_attrs(instances, self.domain.attributes)
        (data,) = instances.to_numpy_MA("A")
        bx = base_term_transform(data, self.cuts, self.dirs, intercept=True)
        return bx

    def base_features(self):
        """
        Return a list of constructed features of Earth terms.

        The features can be used in Orange's domain translation
        (i.e. they define the proper :func:`get_value_from` functions).

        :rtype: list of :class:`Orange.feature.Descriptor`

        """
        terms = []
        dirs = self.dirs[self.best_set]
        cuts = self.cuts[self.best_set]
        # For faster domain translation all the features share
        # this _instance_cache.
        _instance_cache = {}
        for dir, cut in zip(dirs[1:], cuts[1:]):  # Drop the intercept
            hinge = [_format_knot(attr.name, dir1, cut1)
                     for (attr, dir1, cut1) in
                     zip(self.domain.attributes, dir, cut)
                     if dir1 != 0.0]
            term_name = " * ".join(hinge)
            term = Orange.feature.Continuous(term_name)
            term.get_value_from = term_computer(
                term, self.domain, dir, cut,
                _instance_cache=_instance_cache
            )

            terms.append(term)
        return terms

    def predict(self, instance):
        """
        Predict the response values.

        :param Orange.data.Instance instance:
            Data instance

        """
        data = Orange.data.Table(self.domain, [instance])
        bx = self.base_matrix(data)
        bx_used = bx[:, self.best_set]
        vals = numpy.dot(bx_used, self.betas.T).ravel()
        return vals

    def used_attributes(self, term=None):
        """
        Return the used features in `term` (index).

        If no term is given, return all features used in the model.

        :param int term: Term index

        """
        if term is None:
            return reduce(set.union, [self.used_attributes(i) \
                                      for i in range(self.best_set.size)],
                          set())

        attrs = self.domain.attributes

        used_mask = self.dirs[term, :] != 0.0
        return [a for a, u in zip(attrs, used_mask) if u]

    def evimp(self, used_only=True):
        """
        Return the estimated variable importances.

        :param bool used_only: If True return only used attributes.

        """
        return evimp(self, used_only)

    def __reduce__(self):
        return (type(self), (self.domain, self.best_set, self.dirs,
                            self.cuts, self.betas),
                dict(self.__dict__))

    def to_string(self, precision=3, indent=3):
        """
        Return a string representation of the model.

        This is also the default string representation of the model
        (as returned by :func:`str`)

        """
        if self.multitarget:
            r_vars = list(self.domain.class_vars)
        elif is_discrete(self.class_var):
            r_vars = self.expanded_class
        else:
            r_vars = [self.class_var]

        feature_names = [f.name for f in self.domain.features]
        r_names = [v.name for v in r_vars]
        betas = self.betas

        resp = []
        for name, betas in zip(r_names, betas):
            resp.append(
                _format_response(name, betas, self.cuts[self.best_set],
                                 self.dirs[self.best_set], feature_names,
                                 precision, indent))

        return "\n\n".join(resp)

    def __str__(self):
        return self.to_string()


def _format_response(resp_name, betas, cuts, dirs, pred_names,
                     precision=3, indent=3):
    header = "%s =" % resp_name
    indent = " " * indent
    fmt = "%." + str(precision) + "f"
    terms = [([], fmt % betas[0])]  # Intercept

    for beta, cut1, dir1 in zip(betas[1:], cuts[1:], dirs[1:]):
        knots = [_format_knot(name, d, c, precision)
                 for d, c, name in zip(dir1, cut1, pred_names)
                 if d != 0]
        term_attrs = [name for name, d in zip(pred_names, dir1) if d != 0]
        sign = "-" if beta < 0 else "+"
        beta = fmt % abs(beta)
        if knots:
            terms.append((term_attrs,
                          sign + " * ".join([beta] + knots)))
        else:
            raise Exception

    terms = sorted(terms, key=lambda t: len(t[0]))
    return "\n".join([header] + [indent + t for _, t in terms])


def _format_knot(name, direction, cut, precision=3):
    fmt = "%%.%if" % precision
    if direction == 1:
        txt = ("max(0, %s - " + fmt + ")") % (name, cut)
    elif direction == -1:
        txt = ("max(0, " + fmt + " - %s)") % (cut, name)
    elif direction == 2:
        txt = name
    return txt


class term_computer(Orange.core.ClassifierFD):
    """
    An utility class for computing basis terms. Can be used as
    a :obj:`~Orange.feature.Descriptior.get_value_from` member.

    """
    def __init__(self, term_var=None, domain=None, dirs=None, cuts=None,
                 _instance_cache=None):
        self.class_var = term_var
        self.domain = domain

        self.dirs = dirs
        self.cuts = cuts

        self.mask = self.dirs != 0
        self.masked_dirs = numpy.ascontiguousarray(self.dirs[self.mask])
        self.masked_cuts = numpy.ascontiguousarray(self.cuts[self.mask])

        self._instance_cache = _instance_cache

    def __call__(self, instance, return_what=Orange.core.GetValue):
        instance = self._instance_as_masked_array(instance)

        values = instance[self.mask]
        if numpy.ma.is_masked(values):
            # Can't compute the term.
            return self.class_var("?")

        # Works faster with contiguous arrays
        values = numpy.ascontiguousarray(values)
        values -= self.masked_cuts
        values *= self.masked_dirs

        values[values < 0] = 0
        value = numpy.prod(values)

        return self.class_var(value)

    def _instance_as_masked_array(self, instance):
        array = None
        if self._instance_cache is not None:
            array = self._instance_cache.get(instance, None)

        if array is None:
            table = Orange.data.Table(self.domain, [instance])
            (array,) = table.to_numpy_MA("A")
            array = array[0]

            if self._instance_cache is not None:
                self._instance_cache.clear()
                self._instance_cache[instance] = array
        return array

    def __reduce__(self):
        return (type(self),
                (self.class_var, self.domain, self.dirs, self.cuts),
                dict(self.__dict__.items()))


from .evimp import evimp, bagged_evimp, ScoreEarthImportance
