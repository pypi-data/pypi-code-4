from utils import *
from utils import _set_types
from utils import _gsl_check_status, _gsl_check_null_pointer


#### ORDINARY DIFFERENTIAL EQUATIONS

_GSL_ODE_FUNC_TYPE = CFUNCTYPE(c_int, c_double,
                               POINTER(c_double),
                               POINTER(c_double),
                               py_object)
_GSL_ODE_JACOBIAN_TYPE = CFUNCTYPE(c_int, c_double,
                                   POINTER(c_double),
                                   POINTER(c_double),
                                   POINTER(c_double),
                                   py_object)
class gsl_odeiv_system(Structure):
    _fields_ = [("function", _GSL_ODE_FUNC_TYPE),
                ("jacobian", _GSL_ODE_JACOBIAN_TYPE),
                ("dimension", c_size_t),
                ("params", py_object)]


# types of steppers
class gsl_odeiv_step_type(Structure):
    pass
_STEP_TYPE_PTR = POINTER(gsl_odeiv_step_type)

odeiv_step_rk2 =     _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk2")
odeiv_step_rk4 =     _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk4")
odeiv_step_rkf45 =   _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rkf45")
odeiv_step_rkck =    _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rkck")
odeiv_step_rk8pd =   _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk8pd")
odeiv_step_rk2imp =  _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk2imp")
odeiv_step_rk2simp = _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk2simp")
odeiv_step_rk4imp =  _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_rk4imp")
odeiv_step_bsimp =   _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_bsimp")
odeiv_step_gear1 =   _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_gear1")
odeiv_step_gear2 =   _STEP_TYPE_PTR.in_dll(libgsl, "gsl_odeiv_step_gear2")

class gsl_odeiv_step(Structure):
    pass

_set_types("odeiv_step_alloc", POINTER(gsl_odeiv_step), [_STEP_TYPE_PTR, c_size_t])
_set_types("odeiv_step_free", None, [POINTER(gsl_odeiv_step)])
_set_types("odeiv_step_reset", _gsl_check_status, [POINTER(gsl_odeiv_step)])
_set_types("odeiv_step_apply", _gsl_check_status, [POINTER(gsl_odeiv_step),
                                                            c_double, c_double,
                                                            POINTER(c_double),
                                                            POINTER(c_double),
                                                            POINTER(c_double),
                                                            POINTER(c_double),
                                                            POINTER(gsl_odeiv_system)  ])

class gsl_odeiv_control(Structure):
    pass
_set_types("odeiv_control_standard_new", POINTER(gsl_odeiv_control), [c_double, c_double, c_double, c_double])
_set_types("odeiv_control_y_new", POINTER(gsl_odeiv_control), [c_double, c_double])
_set_types("odeiv_control_yp_new", POINTER(gsl_odeiv_control), [c_double, c_double])
_set_types("odeiv_control_scaled_new", POINTER(gsl_odeiv_control), [c_double, c_double, c_double, c_double,
                                                                             POINTER(c_double), c_size_t])
_set_types("odeiv_control_free", None, [POINTER(gsl_odeiv_control)])
_set_types("odeiv_control_init", POINTER(gsl_odeiv_control), [c_double, c_double, c_double, c_double])

class gsl_odeiv_evolve(Structure):
    pass
_set_types("odeiv_evolve_alloc", POINTER(gsl_odeiv_evolve), [c_size_t])
_set_types("odeiv_evolve_free",  None, [POINTER(gsl_odeiv_evolve)])
_set_types("odeiv_evolve_reset",  _gsl_check_status, [POINTER(gsl_odeiv_evolve)])
_set_types("odeiv_evolve_apply",  _gsl_check_status, [POINTER(gsl_odeiv_evolve),
                                                               POINTER(gsl_odeiv_control),
                                                               POINTER(gsl_odeiv_step),
                                                               POINTER(gsl_odeiv_system),
                                                               POINTER(c_double),
                                                               c_double,
                                                               POINTER(c_double),
                                                               POINTER(c_double)
                                                               ])


# top level class
class odeiv_system:
    def __init__(self, function, jacobian, dim, step_type, params = None,
                 control_type = "y_new", eps_abs = 1e-6, eps_rel = 0, a_y = 1, a_dydt = 0, scale_abs = None):
        self.libgsl = libgsl # help during __del__
        self.function = function
        self.wrapped_function = _GSL_ODE_FUNC_TYPE(function)
        self.jacobian = jacobian
        if jacobian is not None:
            self.wrapped_jacobian = _GSL_ODE_JACOBIAN_TYPE(jacobian)
        else:
            self.wrapped_jacobian = cast(None, _GSL_ODE_JACOBIAN_TYPE)
        self.dim = dim
        self.params = params
        self.eps_abs = eps_abs
        self.eps_rel = eps_rel
        self.a_y = a_y
        self.a_dydt = a_dydt
        if scale_abs is None:
            scale_abs = [1] * dim
        self.scale_abs = (c_double * dim)(*scale_abs)
        self.gsl_odeiv_sys = gsl_odeiv_system(self.wrapped_function,
                                              self.wrapped_jacobian,
                                              dim, py_object(params))
        if step_type == odeiv_step_bsimp and jacobian is None:
            raise RuntimeError("bsimp stepper requires Jacobian")
        self.stepper  = libgsl.gsl_odeiv_step_alloc(step_type, dim)
        _gsl_check_null_pointer(self.stepper)
        self.t        = 0
        self.y        = (c_double * dim)(*([0.0] * dim))
        self.y_err    = (c_double * dim)(*([0.0] * dim))
        self.dydt_in  = (c_double * dim)(*([0.0] * dim)) # used for simple stepping
        self.dydt_out = (c_double * dim)(*([0.0] * dim)) # used for simple stepping
        self.h = None # current step
        self.control_type = "control_type"
        if control_type == "y_new":
            self.control = libgsl.gsl_odeiv_control_y_new(self.eps_abs, self.eps_rel)
        elif control_type == "yp_new":
            self.control = libgsl.gsl_odeiv_control_yp_new(self.eps_abs, self.eps_rel)
        elif control_type == "standard":
            self.control = libgsl.gsl_odeiv_control_standard_new(self.eps_abs, self.eps_rel,
                                                                 self.a_y, self.a_dydt)
        elif control_type == "scaled":
            self.control = libgsl.gsl_odeiv_control_scaled_new(self.eps_abs, self.eps_rel,
                                                               self.a_y, self.a_dydt,
                                                               self.scale_abs, self.dim)
        else:
            raise RuntimeError("Unsupported control type")
        _gsl_check_null_pointer(self.control)
        self.evolver = libgsl.gsl_odeiv_evolve_alloc(self.dim)
        _gsl_check_null_pointer(self.evolver)
    def __del__(self):
        if self.control is not None:
            self.libgsl.gsl_odeiv_control_free(self.control)
        if self.evolver is not None:
            self.libgsl.gsl_odeiv_evolve_free(self.evolver)
        self.libgsl.gsl_odeiv_step_free(self.stepper)
    def fn_eval(self, t, y, dydt = None):
        """Evaluates the ODE system function.

        The result is put in dydt.  If it is None, the a double array
        is allocated."""
        if dydt is None:
            dydt = (c_double * self.dim)()
        self.function(t, y, dydt, self.params)
        return dydt

    def init(self, t, y):
        """Initialize for new starting time and boundary conditions."""
        self.t = t
        self.y[:] = y
        self.y_err = (c_double * self.dim)(*([0.0] * self.dim))
        self.fn_eval(t, self.y, self.dydt_in)
        self.h = None
        libgsl.gsl_odeiv_step_reset(self.stepper)
        libgsl.gsl_odeiv_evolve_reset(self.evolver)
    
    def step(self, h):
        """Simple stepping: compute values at t + h"""
        libgsl.gsl_odeiv_step_apply(self.stepper, self.t, h, self.y, self.y_err,
                                    self.dydt_in, self.dydt_out, self.gsl_odeiv_sys)
        self.dydt_in, self.dydt_out = self.dydt_out, self.dydt_in
        self.t += h
        
    def evolve(self, t1, h = None):
        """Evolve the system until next time step t1."""
        assert t1 > self.t
        t_tmp = c_double(self.t)
        if h is not None:
            self.h = c_double(h)
        if self.h is None:
            self.h = c_double(t1 - self.t)
        while t_tmp.value < t1:
            libgsl.gsl_odeiv_evolve_apply(self.evolver, self.control, self.stepper, self.gsl_odeiv_sys,
                                          byref(t_tmp), t1, byref(self.h), self.y)
        self.t = t_tmp.value

    def get_y(self):
        return list(self.y[0:self.dim])
    def get_y_err(self):
        return list(self.y_err[0:self.dim])
    
    def __str__(self):
        y_str = str(["%6f" % x for x in self.get_y()])
        y_err_str = str(["%6g" % x for x in self.get_y_err()])
        s = "at " + str(self.t) + ":  y = " + y_str + " +/- " + y_err_str
        return s
