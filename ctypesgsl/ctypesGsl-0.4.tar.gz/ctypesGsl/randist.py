from utils import *
from utils import _set_types, _add_function
from utils import _gsl_check_null_pointer, _gsl_check_status

from ctypes import sizeof

from rng import gsl_rng



def _add_distr_functions(distr_name, params, discrete = False):
    prefixes = ["ran", "ran", "cdf", "cdf", "cdf", "cdf"]
    suffixes = ["", "_pdf", "_P", "_Q", "_Pinv", "_Qinv"]
    if discrete:
        args = [[POINTER(gsl_rng)], [c_uint], [c_uint], [c_uint], [c_double], [c_double]]
        ret =  [c_uint, c_double, c_double, c_double, c_double, c_double]
    else:
        args = [[POINTER(gsl_rng)], [c_double], [c_double], [c_double], [c_double], [c_double]]
        ret =  [c_double] * len(prefixes)
    for r, p, s, args in zip(ret, prefixes, suffixes, args):
        fname = p + "_" + distr_name + s
        #print "testing", fname
        if hasattr(libgsl, "gsl_" + fname):
            #print "adding", fname
            _add_function(fname, r, args + params, globals())


_no_param_distr = ["ugaussian", "landau"]
_one_param_distr = ["gaussian", "ugaussian_tail", "exponential", "laplace", "cauchy",
                    "rayleigh", "chisq", "tdist", "logistic"]
_two_param_distr = ["gaussian_tail", "exppow", "rayleigh_tail", "levy", "gamma",
                    "flat", "lognormal", "fdist", "beta", "pareto", "weibull", "gumbel1",
                    "gumbel2"]
_three_param_distr = ["levy_skew"]
_one_param_discrete = ["poisson", "bernoulli", "geometric", "logarithmic"]
_two_param_discrete = ["negative_binomial"]

for _distr_name in _no_param_distr:
    _add_distr_functions(_distr_name, [])
for _distr_name in _one_param_distr:
    _add_distr_functions(_distr_name, [c_double])
for _distr_name in _two_param_distr:
    _add_distr_functions(_distr_name, [c_double, c_double])
for _distr_name in _three_param_distr:
    _add_distr_functions(_distr_name, [c_double, c_double, c_double])
for _distr_name in _one_param_discrete:
    _add_distr_functions(_distr_name, [c_double], discrete = True)
for _distr_name in _two_param_discrete:
    _add_distr_functions(_distr_name, [c_double, c_double], discrete = True)

# extra functions
_add_function("ran_gaussian_ziggurat", c_double, [POINTER(gsl_rng), c_double], globals())
_add_function("ran_gaussian_ratio_method", c_double, [POINTER(gsl_rng), c_double], globals())
_add_function("ran_ugaussian_ratio_method", c_double, [POINTER(gsl_rng)], globals())

_set_types("ran_bivariate_gaussian", None, [POINTER(gsl_rng), c_double, c_double, c_double,
                                            POINTER(c_double), POINTER(c_double)])
def ran_bivariate_gaussian(rng, sigma_x, sigma_y, rho):
    ret_x = c_double()
    ret_y = c_double()
    libgsl.gsl_ran_bivariate_gaussian(rng.ptr, sigma_x, sigma_y, rho, byref(ret_x), byref(ret_y))
    return ret_x.value, ret_y.value
_add_function("ran_bivariate_gaussian_pdf", c_double, [c_double, c_double, c_double, c_double, c_double], globals())

_add_distr_functions("binomial", [c_double, c_uint], discrete = True)
_add_distr_functions("pascal", [c_double, c_uint], discrete = True)
_add_distr_functions("hypergeometric", [c_uint, c_uint, c_uint], discrete = True)


# spherical distributions
_set_types("ran_dir_2d", None, [POINTER(gsl_rng), POINTER(c_double), POINTER(c_double)])
def ran_dir_2d(rng):
    ret_x = c_double()
    ret_y = c_double()
    libgsl.gsl_ran_dir_2d(rng.ptr, byref(ret_x), byref(ret_y))
    return ret_x.value, ret_y.value
_set_types("ran_dir_2d_trig_method", None, [POINTER(gsl_rng), POINTER(c_double), POINTER(c_double)])
def ran_dir_2d_trig_method(rng):
    ret_x = c_double()
    ret_y = c_double()
    libgsl.gsl_ran_dir_2d_trig_method(rng.ptr, byref(ret_x), byref(ret_y))
    return ret_x.value, ret_y.value
_set_types("ran_dir_3d", None, [POINTER(gsl_rng), POINTER(c_double), POINTER(c_double), POINTER(c_double)])
def ran_dir_3d(rng):
    ret_x = c_double()
    ret_y = c_double()
    ret_z = c_double()
    libgsl.gsl_ran_dir_2d(rng.ptr, byref(ret_x), byref(ret_y), byref(ret_z))
    return ret_x.value, ret_y.value, ret_z.value
_set_types("ran_dir_nd", None, [POINTER(gsl_rng), c_size_t, POINTER(c_double)])
def ran_dir_nd(rng, n):
    ret_x = (c_double * n)()
    libgsl.gsl_ran_dir_nd(rng.ptr, n, ret_x)
    return list(ret_x)

# dirichlet distribution
_set_types("ran_dirichlet", None, [POINTER(gsl_rng), c_size_t, POINTER(c_double), POINTER(c_double)])
def ran_dirichlet(rng, alpha):
    K = len(alpha)
    alpha_c = (c_double * K)(*alpha)
    theta = (c_double * K)()
    libgsl.gsl_ran_dirichlet(rng.ptr, K, alpha_c, theta)
    return list(theta)
_set_types("ran_dirichlet_pdf", c_double, [c_size_t, POINTER(c_double), POINTER(c_double)])
def ran_dirichlet_pdf(alpha, theta):
    K = len(alpha)
    alpha_c = (c_double * K)(*alpha)
    theta_c = (c_double * K)(*theta)
    return libgsl.gsl_ran_dirichlet_pdf(K, alpha_c, theta_c)
_set_types("ran_dirichlet_lnpdf", c_double, [c_size_t, POINTER(c_double), POINTER(c_double)])
def ran_dirichlet_lnpdf(alpha, theta):
    K = len(alpha)
    alpha_c = (c_double * K)(*alpha)
    theta_c = (c_double * K)(*theta)
    return libgsl.gsl_ran_dirichlet_lnpdf(K, alpha_c, theta_c)

# multinomial distribution
_set_types("ran_multinomial", None, [POINTER(gsl_rng), c_size_t, c_uint, POINTER(c_double), POINTER(c_uint)])
def ran_multinomial(rng, N, p):
    K = len(p)
    p_c = (c_double * K)(*p)
    n = (c_uint * K)()
    libgsl.gsl_ran_multinomial(rng.ptr, K, N, p_c, n)
    return list(n)
_set_types("ran_multinomial_pdf", c_double, [c_size_t, POINTER(c_double), POINTER(c_uint)])
def ran_multinomial_pdf(p, n):
    if len(p) != len(n):
        raise RuntimeError("parameter lenghts don't match")
    K = len(p)
    p_c = (c_double * K)(*p)
    n_c = (c_uint * K)(*n)
    return libgsl.gsl_ran_multinomial_pdf(K, p_c, n_c)
_set_types("ran_multinomial_lnpdf", c_double, [c_size_t, POINTER(c_double), POINTER(c_uint)])
def ran_multinomial_lnpdf(p, n):
    if len(p) != len(n):
        raise RuntimeError("parameter lenghts don't match")
    K = len(p)
    p_c = (c_double * K)(*p)
    n_c = (c_uint * K)(*n)
    return libgsl.gsl_ran_multinomial_lnpdf(K, p_c, n_c)



# general discrete distributions

class gsl_ran_discrete_t(Structure):
    pass

_set_types("ran_discrete_preproc", POINTER(gsl_ran_discrete_t), [c_size_t, POINTER(c_double)])
_set_types("ran_discrete_free", None, [POINTER(gsl_ran_discrete_t)])
_set_types("ran_discrete", c_size_t, [POINTER(gsl_rng), POINTER(gsl_ran_discrete_t)])
_set_types("ran_discrete_pdf", c_double, [c_size_t, POINTER(gsl_ran_discrete_t)])


class ran_discrete(object):
    def __init__(self, P):
        self.libgsl = libgsl
        self.K = len(P)
        P_c = (c_double * self.K)(*P)
        self.ptr = libgsl.gsl_ran_discrete_preproc(len(P_c), P_c)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_ran_discrete_free(self.ptr)

    def get(self, rng):
        return libgsl.gsl_ran_discrete(rng.ptr, self.ptr)
    def __call__(self, rng):
        return self.get(rng)

    def pdf(self, k = None):
        if k is not None:
            return libgsl.gsl_ran_discrete_pdf(k, self.ptr)
        return [libgsl.gsl_ran_discrete_pdf(k, self.ptr) for k in xrange(self.K)]


# sampling shuffling etc.

# needs a hack: GSL functions are applied to arrays of size_t, which
# are then used to shuffle Python containers.  This guarantees results
# identical to GSL

_set_types("ran_shuffle", None, [POINTER(gsl_rng), c_void_p, c_size_t, c_size_t])
def ran_shuffle(rng, seq):
    """Shuffle the sequence seq.

    Returns a new list with elements of seq in random order."""
    n = len(seq)
    # create a sequence 
    idx = (c_size_t * n)()
    for i in xrange(n):
        idx[i] = i
    libgsl.gsl_ran_shuffle(rng.ptr, idx, n, sizeof(c_size_t))
    result_list = [seq[i] for i in idx]
    return result_list

_set_types("ran_choose", _gsl_check_status, [POINTER(gsl_rng), c_void_p, c_size_t, c_void_p, c_size_t, c_size_t])
def ran_choose(rng, k, src):
    """Sample without replacement.

    Returns a new list of selected elements."""
    n = len(src)
    # create a sequence 
    idx_src = (c_size_t * n)()
    for i in xrange(n):
        idx_src[i] = i
    idx_target = (c_size_t * k)()
    libgsl.gsl_ran_choose(rng.ptr, idx_target, k, idx_src, n, sizeof(c_size_t))
    result_list = [src[i] for i in idx_target]
    return result_list
_set_types("ran_sample", None, [POINTER(gsl_rng), c_void_p, c_size_t, c_void_p, c_size_t, c_size_t])
def ran_sample(rng, k, src):
    """Sample with replacement.

    Returns a new list of selected elements."""
    n = len(src)
    # create a sequence 
    idx_src = (c_size_t * n)()
    for i in xrange(n):
        idx_src[i] = i
    idx_target = (c_size_t * k)()
    libgsl.gsl_ran_sample(rng.ptr, idx_target, k, idx_src, n, sizeof(c_size_t))
    result_list = [src[i] for i in idx_target]
    return result_list
