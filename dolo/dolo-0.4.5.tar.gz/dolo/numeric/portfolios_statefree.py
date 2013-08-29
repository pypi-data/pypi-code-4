from dolo import Parameter
from dolo.symbolic.symbolic import Variable, TSymbol, Shock
from dolo.numeric.perturbations import solve_decision_rule
import numpy

from dolo import Equation
import sympy

def standardize_portfolio_model(model_pf):

    model = model_pf.copy()

    zipped = [(i,eq.tags.get('portfolio')) for i,eq in enumerate(model.equations) if eq.tags.get('portfolio') is not None]
    [pf_eqs_inds, pf_vars] = zip(*zipped)
    pf_vars = [Variable(s) for s in pf_vars]

    xi = Shock('xi')
    i_eq_xi = [ i for i,eq in enumerate(model.equations) if enumerate(model.equations) if xi in eq.atoms()]

    assert(len(i_eq_xi)==1)
    i_eq_xi = i_eq_xi[0]

    pred_vars = [v for v in model.predetermined_variables if v not in pf_vars]

    n_pf = len(pf_vars)
    n_p = len(pred_vars)

    matpred = sympy.Matrix( n_p, 1, lambda i,j: pred_vars[i](-1) )
    const = sympy.Matrix( n_pf, 1, lambda i,j: Parameter('KK_{}'.format(i)) )
    coeffs = sympy.Matrix( n_pf, n_p, lambda i,j: Parameter('CC_{}_{}'.format(i,j)) )

    new_parameters = const[:] + coeffs[:]
    model.symbols_s['parameters'].extend(new_parameters)

    model.calibration_s.update({s: 0 for s in new_parameters})

    shifted_vars = {v(-1):v for v in pf_vars}
    shifted_vars.update({v:v(1) for v in pf_vars})

    D = []
    R = []

    vv = const + coeffs*matpred
    equations = model.equations_groups['dynare_block']

    for n,eq in enumerate( equations ):
        if 'portfolio' not in eq.tags:
            eqq  = eq.subs(shifted_vars)
        else:
            # some checks
            D.append(model.variables.index(eq.gap.args[0].P))
            R.append(model.variables.index(eq.gap.args[1].P))
            pfn = eq.tags.get('portfolio')
            s = Variable( pfn )
            i_pf = pf_vars.index(s)
            tt =  vv[i_pf]
            eqq = Equation( s,tt )

        equations[n] = eqq

    model.update()

    return [model, pf_eqs_inds, pf_vars, D, R, i_eq_xi, const, coeffs]

def solve_given_portolios(model, pf_eqs_ind, pf_vars, D, R, i_eq_xi, coeffs_s, coeffs_s_d, coeffs, coeffs_d, diff=False):

    for i in range( coeffs_s.shape[0] ):
        model.calibration_s[coeffs_s[i]] = float( coeffs[i] )
        model.calibration_s[pf_vars[i]] = float( coeffs[i] )
        for j in range(coeffs_s_d.shape[1]):
            model.calibration_s[coeffs_s_d[i,j]] = float( coeffs_d[i,j] )

    model.update()

    D = D[0:1]
    if not diff:
        dr = solve_decision_rule(model, check_residuals=False)
        sigma = dr['Sigma']

        R1 = dr['g_e'][R, -1]
        D1 = dr['g_e'][D, -1]

        R2 = dr['g_e'][R, :][:,:]
        D2 = dr['g_e'][D, :][0,:]

        res = numpy.zeros((R1.shape[0],))
        for i in range(len(res)):
            res[i] = numpy.dot( D2, numpy.dot(sigma, R2[i,:].T))

        return res*100
        # lam_u = D1 * numpy.dot(R2, numpy.dot(sigma, R2.T) )
        # dd = numpy.dot( numpy.dot(R2,sigma), D2.T )[None,:]*R1[:,None]
        #
        # lam_u = lam_u  + dd
        #
        # from numpy.linalg import solve
        #
        # alpha = -solve(lam_u, res)
        #
        # return alpha

    else:

        pred_ind = numpy.array([model.variables.index(e) for e in model.predetermined_variables])

        dr = solve_decision_rule(model, check_residuals=False, order=2)
        sigma = dr['Sigma']
        A = dr['g_e'][D, :]
        B = dr['g_e'][R, :]
        dA = dr['g_ae'][D, :,:][:,pred_ind,:]
        dB = dr['g_ae'][R, :,:][:,pred_ind,:]
        dres = numpy.zeros((B.shape[0],dB.shape[1]))
        for i in range(dres.shape[0]):
            dres[i,:] = numpy.dot( A[0,:], numpy.dot(sigma, dB[i,:,:].T)) + numpy.dot( B[i,:], numpy.dot(sigma, dA[0,:,:].T))

        #index of predetermined variables

        return dres*100



if __name__ == '__main__':

    # filename = '/home/pablo/Documents/Research/CGR/revival/CKM.mod'

    # filename = '/home/pablo/Programmation/dynare/examples/portfolios/example1.mod'
    filename = '/home/pablo/Programmation/dynare/examples/portfolios/CKM2.mod'
    # filename = '/home/pablo/Programmation/dynare/examples/portfolios/example2.mod'

    from copy import copy, deepcopy

    import sympy

    from dolo.misc.modfile import dynare_import

    model = dynare_import(filename)
    # print(model.sigma)
    # print model.predetermined_variables

    [model_det, pf_eqs_ind, pf_vars, D, R, i_eq_xi, coeffs_sym, dcoeffs_sym] = standardize_portfolio_model(model)

    import numpy
    start = numpy.zeros( coeffs_sym.shape )
    start_d = numpy.zeros(dcoeffs_sym.shape)

    from dolo.numeric.solver import solver


    fobj  = lambda x: solve_given_portolios(model_det, pf_eqs_ind, pf_vars, D, R, i_eq_xi, coeffs_sym, dcoeffs_sym, x    , start_d , diff=False)
    #                 solve_given_portolios(model,     pf_eqs_ind, pf_vars, D, R, coeffs_s  , coeffs_s_d, coeffs, coeffs_d, diff=False):
    print("Solving constant term")

    print( fobj(start) )

    start = numpy.array([-5,-0.5,0.5])
    from dolo.numeric.newton import simple_newton
    sol = simple_newton(fobj, start.flatten())

    # sol = solver(fobj, start, method='fsolve', verbose=True)
    print(sol)

    fobj2 = lambda zz: solve_given_portolios(model_det, pf_eqs_ind, pf_vars, D, R, i_eq_xi, coeffs_sym, dcoeffs_sym, sol, zz.reshape(start_d.shape), diff=True).flatten()
    print("Solving dynamic term")
    dsol = simple_newton(fobj2, start_d.ravel())
    # dsol = solver(fobj2, start_d.ravel(), method='fsolve', verbose=True )

    print(sol)
    print(dsol)

