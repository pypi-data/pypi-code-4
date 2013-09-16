"""
EARTH interface
"""

from __future__ import division

import ctypes
import numpy

from numpy import ctypeslib

from . import _earth

_c_earth_lib = ctypeslib.load_library(_earth.__file__, "")

_c_earth = _c_earth_lib.Earth

_c_earth.argtypes = [
    # pBestGcv: GCV of the best model.
    ctypes.POINTER(ctypes.c_double),
    # pnTerms: number of terms in the final model
    ctypes.POINTER(ctypes.c_int),
    # BestSet: nMaxTerms x 1, indices of the best set of cols of bx
    ctypeslib.ndpointer(dtype=ctypes.c_bool),
    # bx: nCases x nMaxTerms basis matrix
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # Dirs: nMaxTerms x nPreds, -1,0,1,2 for iTerm, iPred
    ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=2, flags="F_CONTIGUOUS"),
    # Cuts: nMaxTerms x nPreds, cut for iTerm, iPred
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # Residuals: nCases x nResp
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # Betas: nMaxTerms x nResp
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # x: nCases x nPreds
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # y: nCases x nResp
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=2, flags="F_CONTIGUOUS"),
    # WeightsArg: nCases x 1, can be NULL, currently ignored
    ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1),
    # nCases: number of rows in x and elements in y
    ctypes.c_int,
    # nResp: number of cols in y
    ctypes.c_int,
    # nPred: number of cols in x
    ctypes.c_int,
    # nMaxDegree: Friedman's mi
    ctypes.c_int,
    # nMaxTerms: includes the intercept term
    ctypes.c_int,
    # Penalty: GCV penalty per knot
    ctypes.c_double,
    # Thresh: forward step threshold
    ctypes.c_double,
    # nMinSpan: set to non zero to override internal calculation
    ctypes.c_int,
    # Prune: do backward pass
    ctypes.c_bool,
    # nFastK: Fast MARS K
    ctypes.c_int,
    # FastBeta: Fast MARS aging coef
    ctypes.c_double,
    # NewVarPenalty: penalty for adding a new variable
    ctypes.c_double,
    # LinPreds: nPreds x 1, 1 if predictor must enter linearly
    ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=1),
    # UseBetaCache: 1 to use the beta cache, for speed
    ctypes.c_bool,
    # Trace: 0 none 1 overview 2 forward 3 pruning 4 more pruning
    ctypes.c_double,
    # sPredNames: predictor names in trace printfs, can be NULL
    ctypes.c_char_p
]


def forward_pass(x, y, weights=None, degree=1, terms=None, penalty=None,
                 thresh=0.001, min_span=0, fast_k=21, fast_beta=1,
                 new_var_penalty=2, trace=0):
    """
    Earth forward pass.

    Parameters
    ----------
    x : numpy.array
        An N x M array of predictors
    y : numpy.array
        An N x R array of responses
    weights : numpy.array
        An N x 1 array of instance weights (unused)
    degree : int
        Maximum term degree (default 1)
    terms : int
        Maximum number of terms to induce.
    penalty : float
        GCV penalty per knot.
    thresh : float
        RSS stopping threshold.
    min_span: int
    new_var_penalty : int
        Penalty for addin a new variable in the model.
    fast_k : int
    fast_beta : int

    """
    x = numpy.asfortranarray(x, dtype=ctypes.c_double)
    y = numpy.asfortranarray(y, dtype=ctypes.c_double)

    if x.shape[0] != y.shape[0]:
        raise ValueError("First dimensions of x and y must be the same.")

    if y.ndim == 1:
        y = y.reshape((-1, 1), order="F")

    if penalty is None:
        penalty = 3. if degree > 1. else 2.
    elif penalty < 0 and penalty != -1.:
        raise ValueError("Invalid 'penalty'")

    n_cases, n_preds = x.shape

    _, n_resp = y.shape

    # Output variables
    p_best_gcv = ctypes.c_double()
    n_term = ctypes.c_int()
    best_set = numpy.zeros((terms,), dtype=ctypes.c_bool, order="F")
    bx = numpy.zeros((n_cases, terms), dtype=ctypes.c_double, order="F")
    dirs = numpy.zeros((terms, n_preds), dtype=ctypes.c_int, order="F")
    cuts = numpy.zeros((terms, n_preds), dtype=ctypes.c_double, order="F")
    residuals = numpy.zeros((n_cases, n_resp), dtype=ctypes.c_double, order="F")
    betas = numpy.zeros((terms, n_resp), dtype=ctypes.c_double, order="F")

    weights = numpy.ones((n_cases,), dtype=ctypes.c_double, order="F")
    lin_preds = numpy.zeros((n_preds,), dtype=ctypes.c_int, order="F")
    use_beta_cache = True
    prune = False

    # These tests are performed in ForwardPass, and if they fail the function
    # calls exit. So we must check it here and raise a exception to avoid a
    # process shutdown.
    if n_cases < 8:
        raise ValueError("Need at least 8 data instances.")
    if n_cases > 1e8:
        raise ValueError("To many data instances.")
    if n_resp < 1:
        raise ValueError("No response column.")
    if n_resp > 1e6:
        raise ValueError("To many response columns.")
    if n_preds < 1:
        raise ValueError("No predictor columns.")
    if n_preds > 1e5:
        raise ValueError("To many predictor columns.")
    if degree <= 0 or degree > 100:
        raise ValueError("Invalid 'degree'.")
    if terms < 3 or terms > 10000:
        raise ValueError("'terms' must be in >= 3 and <= 10000.")
    if penalty < 0 and penalty != -1:
        raise ValueError("Invalid 'penalty' (the only legal negative value "
                         "is -1).")
    if penalty > 1000:
        raise ValueError("Invalid 'penalty' (must be <= 1000).")
    if thresh < 0.0 or thresh >= 1.0:
        raise ValueError("Invalid 'thresh' (must be in [0.0, 1.0) ).")
    if fast_beta < 0 or fast_beta > 1000:
        raise ValueError("Invalid 'fast_beta' (must be in [0, 1000] ).")
    if new_var_penalty < 0 or new_var_penalty > 10:
        raise ValueError("Invalid 'new_var_penalty' (must be in [0, 10] ).")
    if (numpy.var(y, axis=0) <= 1e-8).any():
        raise ValueError("Variance of y is zero (or near zero).")

    _c_earth(ctypes.byref(p_best_gcv), ctypes.byref(n_term),
             best_set, bx, dirs, cuts, residuals, betas,
             x, y, weights,
             n_cases, n_resp, n_preds,
             degree, terms, penalty, thresh, min_span, prune,
             fast_k, fast_beta, new_var_penalty, lin_preds,
             use_beta_cache, trace, None)

    return n_term.value, best_set, bx, dirs, cuts


def gcv(rss, n, n_effective_params):
    """
    Return the generalized cross validation (GCV).

    .. math:: gcv = rss / (n * (1 - NumEffectiveParams / n) ^ 2)

    Parameters
    ----------
    rss : array_like
        Residual sum of squares.
    n : float
        Number of training instances.
    n_effective_params : array_like
        Number of effective parameters.

    """
    return  rss / (n * (1. - n_effective_params / n) ** 2)


def pruning_pass(bx, y, penalty, max_pruned_terms=None):
    """
    Earth pruning pass.

    Parameters
    ----------
    bx : array_like
        An N x P array basis matrix as induced by :func:`forward_pass`.
    y : array_like
        An N x R array of responses.
    penalty : float
        GCV penalty.
    max_pruned_terms : int
        Maximum number of terms to leave in the model. If `None` then
        all model sizes are considered.

    """

    subsets, rss_vec = subset_selection_xtx(bx, y)

    cases, terms = bx.shape
    assert rss_vec.shape == (terms,)

    # Effective parameters for all subsets sizes (of terms)
    n_effective_params = numpy.arange(terms) + 1.0
    n_effective_params += penalty * (n_effective_params - 1.0) / 2.0

    gcv_vec = gcv(rss_vec, cases, n_effective_params)

    if max_pruned_terms is None:
        max_pruned_terms = terms

    min_i = numpy.argmin(gcv_vec[:max_pruned_terms])

    used = numpy.zeros((terms), dtype=bool)

    used[subsets[min_i, :min_i + 1]] = True

    return used, subsets, rss_vec, gcv_vec


def base_term_transform(X, cuts, directions, intercept=False,
                        out=None):
    """
    Transform a data array onto a set of earth basis terms.

    The terms are defined by an earth model parameterized by
    cuts and directions.

    Parameters
    ----------
    X : array_like
        An N x P input array.
    cuts : array_like
        An T x P array of hinge term knots
    directions : array_like
        An T x P array of hinge term directions.
    intercept : bool
        If True then the first row of directions and cuts is taken to be
        the intercept term (directions[0] must have all 0 elements).

    """
    X = numpy.asanyarray(X)
    directions = numpy.asarray(directions)
    cuts = numpy.asarray(cuts)

    if directions.ndim == 1:
        directions = directions.reshape((1, -1))

    if cuts.ndim == 1:
        cuts = cuts.reshape((1, -1))

    if cuts.shape != directions.shape:
        raise ValueError("'cuts' and 'directions' must have the same shape")

    N, P = X.shape
    M, P_1 = directions.shape
    if P != P_1:
        raise ValueError("Dimension mismatch.")

    if out is None:
        out = numpy.zeros((N, M))
    elif out.shape != (N, M):
        raise ValueError("'out' is of wrong size")

    start_term = 0
    if intercept:
        if numpy.any(directions[0]):
            raise ValueError("")
        out[:, 0] = 1.0

        start_term = 1

    for termi in range(start_term, M):
        term_dirs = directions[termi]
        term_cuts = cuts[termi]

        dir_p1 = numpy.where(term_dirs == 1)[0]
        dir_m1 = numpy.where(term_dirs == -1)[0]
        dir_2 = numpy.where(term_dirs == 2)[0]

        x1 = X[:, dir_p1] - term_cuts[dir_p1]
        x2 = term_cuts[dir_m1] - X[:, dir_m1]
        x3 = X[:, dir_2]

        x1 = numpy.where(x1 > 0.0, x1, 0.0)
        x2 = numpy.where(x2 > 0.0, x2, 0.0)

        Term = numpy.cumprod(numpy.hstack((x1, x2, x3)), axis=1)
        # Term can have a (N, 0) shape if all(term_dirs == 0)
        out[:, termi] = Term[:, -1] if Term.size else 0.0

    return out


def subset_selection_xtx(X, Y, lstsq=None):
    """
    A re-implementation of EvalSubsetsUsingXtx in the Earth c code.

    Using numpy least squares fitter.

    """
    X = numpy.asarray(X)
    Y = numpy.asarray(Y)

    if lstsq is None:
        lstsq = numpy.linalg.lstsq

    n_pred = X.shape[1]
    rss_vec = numpy.zeros(n_pred)
    working_set = range(n_pred)
    subsets = numpy.zeros((n_pred, n_pred), dtype=int)

    for subset_size in reversed(range(n_pred)):
        subsets[subset_size, :subset_size + 1] = working_set
        X_work = X[:, working_set]
        b = lstsq(X_work, Y)[0]

        rss_vec[subset_size] = numpy.sum((Y - numpy.dot(X_work, b)) ** 2)

        XtX = numpy.dot(X_work.T, X_work)
        iXtX = numpy.linalg.pinv(XtX)
        diag = numpy.diag(iXtX).reshape((-1, 1))

        if subset_size == 0:
            break

        delta_rss = b ** 2 / diag
        delta_rss = numpy.sum(delta_rss, axis=1)
        delete_i = numpy.argmin(delta_rss[1:]) + 1  # Keep the intercept
        del working_set[delete_i]

    return subsets, rss_vec
