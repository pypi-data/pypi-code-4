import logging
from math import pi, sqrt

import numpy as np
from numpy.random import rand

import matplotlib.pyplot as plt

from empirical.eim import EI
from empirical.mesh import Mesh1D, Mesh2D


log = logging.getLogger(__name__)


def f(x, mu):
    return np.cos(x * mu)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    mesh = Mesh1D(-pi, pi, N=75, qtype='lgl')
    params = np.linspace(0, 4, 100).reshape((100, 1))
    ei = EI(f, mesh.vector, mesh.vector_weights, params)
    ei.solve(M=25)
    test_params = rand(100) * 4
    norms = []
    m_eim = [i for i in range(5, 26)]
    for m in m_eim:
        max_norm = float('-inf')
        for p in test_params:
            max_norm = max(max_norm, ei.L2_norm(p, M=m))
        norms += [max_norm]

    norms_linear = []
    norms_cc = []
    norms_lgl = []
    for m in m_eim:
        log.info("Processing 2-d interpolation, N=75, M=%s", m)
        mesh_linear = Mesh2D(-pi, pi, 0, 4, N=75, M=m, qtype_x='lgl', qtype_y='linear')
        mesh_cc = Mesh2D(-pi, pi, 0, 4, N=75, M=m, qtype_x='lgl', qtype_y='cc')
        mesh_lgl = Mesh2D(-pi, pi, 0, 4, N=75, M=m, qtype_x='lgl', qtype_y='lgl')
        evals_linear = f(mesh_linear.grid[:, :, 0], mesh_linear.grid[:, :, 1])
        evals_cc = f(mesh_cc.grid[:, :, 0], mesh_cc.grid[:, :, 1])
        evals_lgl = f(mesh_lgl.grid[:, :, 0], mesh_lgl.grid[:, :, 1])
        interp_linear = mesh_linear.interpolate_func(evals_linear)
        interp_cc = mesh_cc.interpolate_func(evals_cc)
        interp_lgl = mesh_lgl.interpolate_func(evals_lgl)

        max_norm_linear = float('-inf')
        max_norm_cc = float('-inf')
        max_norm_lgl = float('-inf')
        i = 0
        for p in test_params:
            i += 1
            linear = np.abs(np.square(f(mesh_linear.x, p).flatten() -
                                      interp_linear(mesh_linear.x, p).flatten()))
            linear = sqrt(np.sum(mesh_linear.w_x * linear))
            cc = np.abs(np.square(f(mesh_cc.x, p).flatten() -
                                  interp_cc(mesh_cc.x, p).flatten()))
            cc = sqrt(np.sum(mesh_cc.w_x * cc))
            lgl = np.abs(np.square(f(mesh_lgl.x, p).flatten() -
                                   interp_lgl(mesh_lgl.x, p).flatten()))
            lgl = sqrt(np.sum(mesh_lgl.w_x * lgl))
            max_norm_linear = max(max_norm_linear, linear)
            max_norm_cc = max(max_norm_cc, cc)
            max_norm_lgl = max(max_norm_lgl, lgl)
        norms_linear += [max_norm_linear]
        norms_cc += [max_norm_cc]
        norms_lgl += [max_norm_lgl]

    print("N  |   EI norm    |   LGL norm   |   CC norm    | linear norm")
    print("---------------------------------------------------------------")
    print("5  | %e | %e | %e | %e" % (norms[0], norms_lgl[0], norms_cc[0], norms_linear[0]))
    print("10 | %e | %e | %e | %e" % (norms[5], norms_lgl[5], norms_cc[5], norms_linear[5]))
    print("15 | %e | %e | %e | %e" % (norms[10], norms_lgl[10], norms_cc[10], norms_linear[10]))
    print("20 | %e | %e | %e | %e" % (norms[15], norms_lgl[15], norms_cc[15], norms_linear[15]))
    print("25 | %e | %e | %e | %e" % (norms[20], norms_lgl[20], norms_cc[20], norms_linear[20]))

    plt.figure("Example 3 L2 norms", figsize=(8, 6))
    plt.plot(m_eim, np.log10(norms), 'k-o', label='EIM')
    plt.plot(m_eim, np.log10(norms_cc), 'g-*', label='CC')
    plt.plot(m_eim, np.log10(norms_lgl), 'r-+', label='LGL')
    plt.plot(m_eim, np.log10(norms_linear), 'b-o', label='Linear')
    plt.legend(loc=0)
    plt.xlim((4, 26))
    plt.ylim((-16, 0))
    plt.xlabel("M")
    plt.ylabel("log_10(max(L2 norm))")
    plt.savefig("example3_l2_norms.png", dpi=120, pad_inches=0)

    plt.figure("Basis functions", figsize=(11, 6))
    plt.subplot(231)
    plt.plot(ei.nodes, ei.Q[:, 0])
    plt.subplot(232)
    plt.plot(ei.nodes, ei.Q[:, 1])
    plt.subplot(233)
    plt.plot(ei.nodes, ei.Q[:, 2])
    plt.subplot(234)
    plt.plot(ei.nodes, ei.Q[:, 3])
    plt.subplot(235)
    plt.plot(ei.nodes, ei.Q[:, 4])
    plt.subplot(236)
    plt.plot(ei.nodes, ei.Q[:, 5])
    plt.savefig("example3_basis_functions.png", dpi=120, pad_inches=0)


    points = np.linspace(-pi, pi, 101)
    plt.figure("Test Function", figsize=(13, 4))
    plt.subplot(131)
    plt.plot(points, f(points, 0))
    plt.subplot(132)
    plt.plot(points, f(points, 2))
    plt.subplot(133)
    plt.plot(points, f(points, 4))
    plt.savefig("example3_test_function.png", dpi=120, pad_inches=0)

    plt.show()
