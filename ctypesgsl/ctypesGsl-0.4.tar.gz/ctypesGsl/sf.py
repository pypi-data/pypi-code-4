from utils import *
from utils import _set_types, _add_function
from utils import _int_to_bool, _gsl_check_status

from cgsl_complex import gsl_complex, complex_abs, complex_arg
from cgsl_complex import complex_polar

# result structures 

class gsl_sf_result(Structure):
    _fields_ = [("val", c_double),
                ("err", c_double)]
    def  __str__(self):
        return str(self.val) + " +/- " + str(self.err)
    def __float__(self):
        return self.val

class gsl_sf_result_e10(Structure):
    _fields_ = [("val", c_double),
                ("err", c_double),
                ("e10", c_int)]
    def  __str__(self):
        return "(" + str(self.val) + " +/- " + str(self.err) + ")*10^" + str(self.e10)


# modes
gsl_mode_t = c_uint

GSL_PREC_DOUBLE = 0
GSL_PREC_SINGLE = 1
GSL_PREC_APPROX = 2


class _sf_wrapper_w_mode(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, x, mode = GSL_PREC_DOUBLE):
        res = gsl_sf_result()
        self.f(x, mode, byref(res))
        return res
class _sf_wrapper2_w_mode(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, x, y, mode = GSL_PREC_DOUBLE):
        res = gsl_sf_result()
        self.f(x, y, mode, byref(res))
        return res
class _sf_wrapper3_w_mode(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, x, y, z, mode = GSL_PREC_DOUBLE):
        res = gsl_sf_result()
        self.f(x, y, z, mode, byref(res))
        return res
class _sf_wrapper4_w_mode(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, x, y, z, t, mode = GSL_PREC_DOUBLE):
        res = gsl_sf_result()
        self.f(x, y, z, t, mode, byref(res))
        return res
class _sf_wrapper_bessel_array(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, nmin, nmax, x):
        fvals = (c_double * (nmax - nmin + 1))()
        self.f(nmin, nmax, x, fvals)
        return fvals[:]
class _sf_wrapper_bessel_array2(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, nmax, x):
        fvals = (c_double * (nmax + 1))()
        self.f(nmax, x, fvals)
        return fvals[:]
class _sf_wrapper_int_float_float_array(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, nmax, x, y):
        fvals = (c_double * (nmax + 1))()
        self.f(nmax, x, y, fvals)
        return fvals[:]
class _sf_wrapper_complex(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, c):
        if not isinstance(c, gsl_complex):
            c = gsl_complex(c)
        res_re = gsl_sf_result()
        res_im = gsl_sf_result()
        self.f(c.real, c.imag, res_re, res_im)
        return gsl_complex(res_re.val, res_im.val)
class _sf_wrapper_complex_e(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, c):
        if not isinstance(c, gsl_complex):
            c = gsl_complex(c)
        res_re = gsl_sf_result()
        res_im = gsl_sf_result()
        self.f(c.real, c.imag, res_re, res_im)
        return gsl_complex(res_re.val, res_im.val), (res_re.err, res_im.err)



_single_arg_w_mode = ['sf_airy_Ai', 'sf_airy_Bi',
                      'sf_airy_Ai_scaled', 'sf_airy_Bi_scaled',
                      'sf_airy_Ai_deriv', 'sf_airy_Bi_deriv',
                      'sf_airy_Ai_deriv_scaled', 'sf_airy_Bi_deriv_scaled',
                      'sf_ellint_Kcomp', 'sf_ellint_Ecomp'
                      ]
_two_arg_w_mode = ['sf_ellint_F', 'sf_ellint_E', #'sf_ellint_Pcomp',
                   'sf_ellint_RC']
_three_arg_w_mode = ['sf_ellint_P', 'sf_ellint_D',
                     'sf_ellint_RD', 'sf_ellint_RF']
_four_arg_w_mode = ['sf_ellint_RJ']

_single_arg = ['sf_bessel_J0', 'sf_bessel_J1',
               'sf_bessel_Y0', 'sf_bessel_Y1',
               'sf_bessel_I0', 'sf_bessel_I1',
               'sf_bessel_I0_scaled', 'sf_bessel_I1_scaled',
               'sf_bessel_K0', 'sf_bessel_K1',
               'sf_bessel_K0_scaled', 'sf_bessel_K1_scaled',
               'sf_bessel_j0', 'sf_bessel_j1', 'sf_bessel_j2',
               'sf_bessel_y0', 'sf_bessel_y1', 'sf_bessel_y2',
               'sf_bessel_i0_scaled', 'sf_bessel_i1_scaled', 'sf_bessel_i2_scaled',
               'sf_bessel_k0_scaled', 'sf_bessel_k1_scaled', 'sf_bessel_k2_scaled',
               'sf_clausen', 'sf_dawson',
               'sf_debye_1', 'sf_debye_2', 'sf_debye_3', 'sf_debye_4', 'sf_debye_5', 'sf_debye_6',
               'sf_dilog',
               'sf_erf', 'sf_erfc', 'sf_log_erfc', 'sf_erf_Z', 'sf_erf_Q', 'sf_hazard',
               'sf_exp', 'sf_expm1', 'sf_exprel', 'sf_exprel_2',
               'sf_expint_E1', 'sf_expint_E2', 'sf_expint_Ei',
               'sf_Shi', 'sf_Chi', 'sf_expint_3', 'sf_Si', 'sf_Ci', 'sf_atanint',
               'sf_fermi_dirac_m1', 'sf_fermi_dirac_0', 'sf_fermi_dirac_1',
               'sf_fermi_dirac_2', 'sf_fermi_dirac_mhalf',
               'sf_fermi_dirac_half', 'sf_fermi_dirac_3half',
               'sf_gamma', 'sf_lngamma', 'sf_gammastar', 'sf_gammainv',
               'sf_lambert_W0', 'sf_lambert_Wm1',
               'sf_legendre_P1', 'sf_legendre_P2', 'sf_legendre_P3',
               'sf_legendre_Q0', 'sf_legendre_Q1',
               'sf_log', 'sf_log_abs', 'sf_log_1plusx', 'sf_log_1plusx_mx',
               'sf_psi', 'sf_psi_1piy', 'sf_psi_1',
               'sf_synchrotron_1', 'sf_synchrotron_2',
               'sf_transport_2', 'sf_transport_3', 'sf_transport_4', 'sf_transport_5',
               'sf_sin', 'sf_cos', 'sf_sinc', 'sf_lnsinh', 'sf_lncosh',
               'sf_zeta', 'sf_zetam1', 'sf_eta',
               ]
_two_arg = ['sf_bessel_Jnu', 'sf_bessel_Ynu',
            'sf_bessel_Inu', 'sf_bessel_Inu_scaled',
            'sf_bessel_Knu', 'sf_bessel_lnKnu', 'sf_bessel_Knu_scaled',
            'sf_hydrogenicR_1',
            'sf_exp_mult', 'sf_fermi_dirac_inc_0',
            'sf_poch', 'sf_lnpoch', 'sf_pochrel',
            'sf_gamma_inc', 'sf_gamma_inc_Q', 'sf_gamma_inc_P',
            'sf_beta', 'sf_lnbeta',
            'sf_gegenpoly_1', 'sf_gegenpoly_2', 'sf_gegenpoly_3', 
            'sf_hyperg_0F1', 
            'sf_laguerre_1', 'sf_laguerre_2', 'sf_laguerre_3',
            'sf_conicalP_half', 'sf_conicalP_mhalf', 'sf_conicalP_0', 'sf_conicalP_1',
            'sf_legendre_H3d_0', 'sf_legendre_H3d_1',
            'sf_hypot',
            'sf_hzeta',
            ]
_three_arg = ['sf_beta_inc', 'sf_hyperg_1F1', 'sf_hyperg_U', 'sf_hyperg_2F0']
_four_arg = ['sf_hyperg_2F1', 'sf_hyperg_2F1_conj',
             'sf_hyperg_2F1_renorm', 'sf_hyperg_2F1_conj_renorm']
_one_arg_e10 = ['sf_exp_e10']
_two_arg_e10 = ['sf_exp_mult_e10']

_uint_one_arg = ['sf_airy_zero_Ai', 'sf_airy_zero_Bi',
                 'sf_airy_zero_Ai_deriv', 'sf_airy_zero_Bi_deriv',
                 'sf_bessel_zero_J0', 'sf_bessel_zero_J1',
                 'sf_exprel_n',
                 'sf_fact', 'sf_doublefact', 'sf_lnfact', 'sf_lndoublefact',
                 ]
_int_one_arg = ['sf_psi_int', 'sf_psi_1_int',
                'sf_zeta_int', 'sf_zetam1_int', 'sf_eta_int',
                ]
_uint_two_arg = ['sf_choose', 'sf_lnchoose']
_int_float = ['sf_bessel_Jn', 'sf_bessel_Yn',
              'sf_bessel_In', 'sf_bessel_In_scaled',
              'sf_bessel_Kn', 'sf_bessel_Kn_scaled',
              'sf_bessel_jl', 'sf_bessel_yl',
              'sf_bessel_il_scaled',
              'sf_bessel_kl_scaled',
              'sf_fermi_dirac_int',
              'sf_taylorcoeff',
              'sf_legendre_Pl', 'sf_legendre_Ql',
              'sf_psi_n',
              ]
_float_int = ['sf_pow_int']
_int_float_float = ['sf_gegenpoly_n','sf_hyperg_U_int',
                    'sf_laguerre_n',
                    'sf_conicalP_sph_reg', 'sf_conicalP_cyl_reg', 'sf_legendre_H3d',
                    ]
_int_int_float = ['sf_hyperg_1F1_int',
                  'sf_legendre_Plm', 'sf_legendre_sphPlm',
                  ]
_one_arg_complex = ['sf_complex_dilog', 'sf_complex_log',
                    'sf_complex_sin', 'sf_complex_cos', 'sf_complex_logsin']


_bessel_array = ['sf_bessel_Jn_array', 'sf_bessel_Yn_array',
                 'sf_bessel_In_array', 'sf_bessel_In_scaled_array',
                 'sf_bessel_Kn_array', 'sf_bessel_Kn_scaled_array',
                 ]
_bessel_array2 = ['sf_bessel_jl_array', 'sf_bessel_jl_steed_array',
                  'sf_bessel_yl_array', 'sf_bessel_il_scaled_array',
                  'sf_bessel_kl_scaled_array',
                  'sf_legendre_Pl_array', 'sf_legendre_Pl_deriv_array',
                 ]
_int_float_float_array = ['sf_gegenpoly_array', 'sf_legendre_H3d_array']

for f in _single_arg_w_mode:
    proto = CFUNCTYPE(c_double, c_double, gsl_mode_t)
    globals()[f] = proto(("gsl_" + f, libgsl), ((1, "x"), (1, "mode", GSL_PREC_DOUBLE)))
    new_f = _set_types(f + '_e', _gsl_check_status, [c_double, gsl_mode_t, POINTER(gsl_sf_result)])
    globals()[f + '_e'] = _sf_wrapper_w_mode(new_f)
for f in _two_arg_w_mode:
    proto = CFUNCTYPE(c_double, c_double, c_double, gsl_mode_t)
    globals()[f] = proto(("gsl_" + f, libgsl), ((1, "x"), (1, "y"), (1, "mode", GSL_PREC_DOUBLE)))
    new_f = _set_types(f + '_e', _gsl_check_status, [c_double, c_double, gsl_mode_t, POINTER(gsl_sf_result)])
    globals()[f + '_e'] = _sf_wrapper2_w_mode(new_f)
for f in _three_arg_w_mode:
    proto = CFUNCTYPE(c_double, c_double, c_double, c_double, gsl_mode_t)
    globals()[f] = proto(("gsl_" + f, libgsl), ((1, "x"), (1, "y"), (1, "z"), (1, "mode", GSL_PREC_DOUBLE)))
    new_f = _set_types(f + '_e', _gsl_check_status, [c_double, c_double, c_double, gsl_mode_t, POINTER(gsl_sf_result)])
    globals()[f + '_e'] = _sf_wrapper3_w_mode(new_f)
for f in _four_arg_w_mode:
    proto = CFUNCTYPE(c_double, c_double, c_double, c_double, c_double, gsl_mode_t)
    globals()[f] = proto(("gsl_" + f, libgsl), ((1, "x"), (1, "y"), (1, "z"), (1, "t"), (1, "mode", GSL_PREC_DOUBLE)))
    new_f = _set_types(f + '_e', _gsl_check_status, [c_double, c_double, c_double, c_double, gsl_mode_t, POINTER(gsl_sf_result)])
    globals()[f + '_e'] = _sf_wrapper4_w_mode(new_f)

for f in _single_arg:
    _add_function(f, c_double, [c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (2, "result")))
for f in _two_arg:
    _add_function(f, c_double, [c_double, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "y"), (2, "result")))
for f in _three_arg:
    _add_function(f, c_double, [c_double, c_double, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "y"), (1, "z"), (2, "result")))
for f in _four_arg:
    _add_function(f, c_double, [c_double, c_double, c_double, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, c_double, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "y"), (1, "z"), (1, "t"), (2, "result")))

for f in _one_arg_e10:
    proto = CFUNCTYPE(_gsl_check_status, c_double, POINTER(gsl_sf_result_e10))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (2, "result")))
for f in _two_arg_e10:
    proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, POINTER(gsl_sf_result_e10))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "y"), (2, "result")))

for f in _uint_one_arg:
    _add_function(f, c_double, [c_uint])
    proto = CFUNCTYPE(_gsl_check_status, c_uint, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (2, "result")))
for f in _int_one_arg:
    _add_function(f, c_double, [c_int])
    proto = CFUNCTYPE(_gsl_check_status, c_int, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (2, "result")))
for f in _uint_two_arg:
    _add_function(f, c_double, [c_uint, c_uint])
    proto = CFUNCTYPE(_gsl_check_status, c_uint, c_uint, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "y"), (2, "result")))

for f in _int_float:
    _add_function(f, c_double, [c_int, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_int, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "n"), (1, "x"), (2, "result")))
for f in _float_int:
    _add_function(f, c_double, [c_double, c_int])
    proto = CFUNCTYPE(_gsl_check_status, c_double, c_int, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "x"), (1, "n"), (2, "result")))
for f in _int_float_float:
    _add_function(f, c_double, [c_int, c_double, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_int, c_double, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "n"), (1, "x"), (1, "y"), (2, "result")))
for f in _int_int_float:
    _add_function(f, c_double, [c_int, c_int, c_double])
    proto = CFUNCTYPE(_gsl_check_status, c_int, c_int, c_double, POINTER(gsl_sf_result))
    globals()[f + '_e'] = proto(("gsl_" + f + "_e", libgsl), ((1, "n1"), (1, "n2"), (1, "x"), (2, "result")))

for f in _one_arg_complex:
    new_f = _set_types(f + "_e", _gsl_check_status, [c_double, c_double,
                                             POINTER(gsl_sf_result), POINTER(gsl_sf_result)])
    globals()[f] = _sf_wrapper_complex(new_f)
    globals()[f + "_e"] = _sf_wrapper_complex_e(new_f)

for f in _bessel_array:
    new_f = _set_types(f, _gsl_check_status, [c_int, c_int, c_double, POINTER(c_double)])
    globals()[f] = _sf_wrapper_bessel_array(new_f)
for f in _bessel_array2:
    new_f = _set_types(f, _gsl_check_status, [c_int, c_double, POINTER(c_double)])
    globals()[f] = _sf_wrapper_bessel_array2(new_f)
for f in _int_float_float_array:
    new_f = _set_types(f, _gsl_check_status, [c_int, c_double, c_double, POINTER(c_double)])
    globals()[f] = _sf_wrapper_int_float_float_array(new_f)


### special cases

# Bessel
_set_types('sf_bessel_sequence_Jnu_e', _gsl_check_status,
           [c_double, gsl_mode_t, c_size_t, POINTER(c_double)])
def sf_bessel_sequence_Jnu(nu, xs, mode = GSL_PREC_DOUBLE):
    n = len(xs)
    c_xs = (c_double * n)(*xs)
    libgsl.gsl_sf_bessel_sequence_Jnu_e(nu, mode, n, c_xs)
    return c_xs[:]

_add_function('sf_bessel_zero_Jnu', c_double, [c_double, c_uint], globals())
proto = CFUNCTYPE(_gsl_check_status, c_double, c_uint, POINTER(gsl_sf_result))
globals()['sf_bessel_zero_Jnu_e'] = proto(("gsl_sf_bessel_zero_Jnu_e", libgsl), ((1, "nu"), (1, "s"), (2, "result")))


# coulomb
_add_function('sf_hydrogenicR', c_double, [c_int, c_int, c_double, c_double], globals())
proto = CFUNCTYPE(_gsl_check_status, c_int, c_int, c_double, c_double, POINTER(gsl_sf_result))
globals()['sf_hydrogenicR_e'] = proto(("gsl_sf_hydrogenicR_e", libgsl), ((1, "n"), (1, "l"), (1, "Z"), (1, "r"), (2, "result")))

class coulomb_wave_FG_result(object):
    pass
_set_types('sf_coulomb_wave_FG_e', _gsl_check_status,
           [c_double, c_double, c_double, c_int,
            POINTER(gsl_sf_result), POINTER(gsl_sf_result),
            POINTER(gsl_sf_result), POINTER(gsl_sf_result),
            POINTER(c_double), POINTER(c_double)])
def sf_coulomb_wave_FG_e(eta, x, L_F, k):
    resF  = gsl_sf_result()
    resFp = gsl_sf_result()
    resG  = gsl_sf_result()
    resGp = gsl_sf_result()
    expF  = c_double()
    expG  = c_double()
    res = coulomb_wave_FG_result()
    res.overlow = False
    try:
        libgsl.gsl_sf_coulomb_wave_FG_e(eta, x, L_F, k, resF, resFp, resG, resGp, byref(expF), byref(expG))
    except GSL_Error, ge:
        if ge.gsl_err_code == GSL_EOVRFLW:
            res.overlow = True
        else:
            raise
    res.F  = resF
    res.Fp = resFp
    res.G  = resG
    res.Gp = resGp
    res.expF = expF.value
    res.expG = expG.value
    return res

_set_types('sf_coulomb_wave_F_array', _gsl_check_status, [c_double, c_int, c_double, c_double,
                                                          POINTER(c_double), POINTER(c_double)])
def sf_coulomb_wave_F_array(L_min, kmax, eta, x):
    fc = (c_double * (kmax + 1))()
    exp = c_double()
    try:
        libgsl.gsl_sf_coulomb_wave_F_array(L_min, kmax, eta, x, fc, byref(exp))
    except GSL_Error, ge:
        if ge.gsl_err_code != GSL_EOVRFLW:
            raise
    return fc[:], exp.value

_set_types('sf_coulomb_wave_FG_array', _gsl_check_status, [c_double, c_int, c_double, c_double,
                                                          POINTER(c_double), POINTER(c_double),
                                                          POINTER(c_double), POINTER(c_double)])
def sf_coulomb_wave_FG_array(L_min, kmax, eta, x):
    fc = (c_double * (kmax + 1))()
    expF = c_double()
    gc = (c_double * (kmax + 1))()
    expG = c_double()
    try:
        libgsl.gsl_sf_coulomb_wave_FG_array(L_min, kmax, eta, x, fc, gc, byref(expG), byref(expF))
    except GSL_Error, ge:
        if ge.gsl_err_code != GSL_EOVRFLW:
            raise
    return fc[:], expF.value, gc[:], expG.value
class coulomb_wave_FGp_array_result(object):
    pass
_set_types('sf_coulomb_wave_FGp_array', _gsl_check_status, [c_double, c_int, c_double, c_double,
                                                            POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                                            POINTER(c_double), POINTER(c_double), POINTER(c_double),])
def sf_coulomb_wave_FGp_array(L_min, kmax, eta, x):
    fc = (c_double * (kmax + 1))()
    fcp = (c_double * (kmax + 1))()
    expF = c_double()
    gc = (c_double * (kmax + 1))()
    gcp = (c_double * (kmax + 1))()
    expG = c_double()
    res = coulomb_wave_FGp_array_result()
    res.overlow = False
    try:
        libgsl.gsl_sf_coulomb_wave_FGp_array(L_min, kmax, eta, x, fc, fcp, gc, gcp, byref(expG), byref(expF))
    except GSL_Error, ge:
        if ge.gsl_err_code != GSL_EOVRFLW:
            raise
        else:
            res.overlow = True
    res.Fa   = fc[:]
    res.Fpa  = fcp[:]
    res.Ga   = gc[:]
    res.Gpa  = gcp[:]
    res.expF = expF.value
    res.expG = expG.value
    return res
    
_set_types('sf_coulomb_wave_sphF_array', _gsl_check_status, [c_double, c_int, c_double, c_double,
                                                             POINTER(c_double), POINTER(c_double)])
def sf_coulomb_wave_sphF_array(L_min, kmax, eta, x):
    fc = (c_double * (kmax + 1))()
    exp = c_double()
    try:
        libgsl.gsl_sf_coulomb_wave_sphF_array(L_min, kmax, eta, x, fc, byref(exp))
    except GSL_Error, ge:
        if ge.gsl_err_code != GSL_EOVRFLW:
            raise
    return fc[:], exp.value


proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, POINTER(gsl_sf_result))
globals()['sf_coulomb_CL_e'] = proto(("gsl_sf_coulomb_CL_e", libgsl), ((1, "L"), (1, "eta"), (2, "result")))
_set_types('sf_coulomb_CL_array', _gsl_check_status, [c_double, c_int, c_double, POINTER(c_double)])
def sf_coulomb_CL_array(Lmin, kmax, eta):
    cl = (c_double * (kmax + 1))()
    libgsl.gsl_sf_coulomb_CL_array(Lmin, kmax, eta, cl)
    return cl[:]


# elementary functions
proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, POINTER(gsl_sf_result))
globals()['sf_multiply_e'] = proto(("gsl_sf_multiply_e", libgsl), ((1, "x"), (1, "y"), (2, "result")))
_set_types('sf_multiply_err_e', _gsl_check_status, [c_double, c_double, c_double, c_double, POINTER(gsl_sf_result)])
def sf_multiply_err_e(x, y):
    res = gsl_sf_result()
    libgsl.gsl_sf_multiply_err_e(x.val, x.err, y.val, y.err, res)
    return res

# elliptic functions
_set_types('sf_elljac_e', _gsl_check_status, [c_double, c_double,
                                              POINTER(c_double),
                                              POINTER(c_double),
                                              POINTER(c_double)])
def sf_elljac(u, m):
    sn = c_double()
    cn = c_double()
    dn = c_double()
    libgsl.gsl_sf_elljac_e(u, m, byref(sn), byref(cn), byref(dn))
    return sn.value, cn.value, dn.value

# exp
_set_types('sf_exp_err_e', _gsl_check_status, [c_double, c_double, POINTER(gsl_sf_result)])
_set_types('sf_exp_err_e10_e', _gsl_check_status, [c_double, c_double, POINTER(gsl_sf_result_e10)])
_set_types('sf_exp_mult_err_e', _gsl_check_status,
           [c_double, c_double, c_double, c_double, POINTER(gsl_sf_result)])
_set_types('sf_exp_mult_err_e10_e', _gsl_check_status,
           [c_double, c_double, c_double, c_double, POINTER(gsl_sf_result_e10)])


def sf_exp_err_e(x):
    res = gsl_sf_result()
    libgsl.gsl_sf_exp_err_e(x.val, x.err, res)
    return res
def sf_exp_err_e10_e(x):
    res = gsl_sf_result_e10()
    libgsl.gsl_sf_exp_err_e10_e(x.val, x.err, res)
    return res
def sf_exp_mult_err_e(x, y):
    res = gsl_sf_result()
    libgsl.gsl_sf_exp_mult_err_e(x.val, x.err, y.val, y.err, res)
    return res
def sf_exp_mult_err_e10_e(x, y):
    res = gsl_sf_result_e10()
    libgsl.gsl_sf_exp_mult_err_e10_e(x.val, x.err, y.val, y.err, res)
    return res

# gamma and related
_set_types('sf_lngamma_sgn_e', _gsl_check_status, [c_double, POINTER(gsl_sf_result), POINTER(c_double)])
def sf_lngamma_sgn_e(x):
    res = gsl_sf_result()
    sgn = c_double()
    libgsl.gsl_sf_lngamma_sgn_e(x, res, byref(sgn))
    return sgn.value, res

_set_types('sf_lngamma_complex_e', _gsl_check_status, [c_double, c_double,
                                                       POINTER(gsl_sf_result),
                                                       POINTER(gsl_sf_result)])
def sf_lngamma_complex_e_polar(c):
    if not isinstance(c, gsl_complex):
        c = gsl_complex(c)
    res_r = gsl_sf_result()
    res_i = gsl_sf_result()
    libgsl.gsl_sf_lngamma_complex_e(c.real, c.imag, res_r, res_i)
    return res_r, res_i
def sf_lngamma_complex(c):
    if not isinstance(c, gsl_complex):
        c = gsl_complex(c)
    res_r = gsl_sf_result()
    res_i = gsl_sf_result()
    libgsl.gsl_sf_lngamma_complex_e(c.real, c.imag, res_r, res_i)
    return complex_polar(res_r, res_i)

_set_types('sf_lnpoch_sgn_e', _gsl_check_status, [c_double, c_double, POINTER(gsl_sf_result), POINTER(c_double)])
def sf_lnpoch_sgn_e(a, x):
    res = gsl_sf_result()
    sgn = c_double()
    libgsl.gsl_sf_lnpoch_sgn_e(a, x, res, byref(sgn))
    return sgn.value, res

# hypergeometric
proto = CFUNCTYPE(_gsl_check_status, c_int, c_int, c_double, POINTER(gsl_sf_result_e10))
globals()["sf_hyperg_U_int_e10_e"] = proto(("gsl_sf_hyperg_U_int_e10_e", libgsl), ((1, "m"), (1, "n"), (1, "x"), (2, "result")))

proto = CFUNCTYPE(_gsl_check_status, c_double, c_double, c_double, POINTER(gsl_sf_result_e10))
globals()["sf_hyperg_U_e10_e"] = proto(("gsl_sf_hyperg_U_e10_e", libgsl), ((1, "a"), (1, "b"), (1, "x"), (2, "result")))


