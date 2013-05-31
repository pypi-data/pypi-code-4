import logging
from math import sqrt

import numpy as np
from numpy.random import rand

import matplotlib.pyplot as plt

from empirical.eim import EI
from empirical.mesh import Mesh2D


log = logging.getLogger(__name__)


def f(x, mu1, mu2):
    x1 = x[..., 0]
    x2 = x[..., 1]
    return 1.0 / np.sqrt(np.square(x1 - mu1) + np.square(x2 - mu2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    mesh = Mesh2D(0, 1, 0, 1, N=75, M=75, qtype_x='lgl', qtype_y='lgl')
    params = Mesh2D(-1, -0.01, -1, -0.01, N=50, M=50,
                     qtype_x='linear', qtype_y='linear')
    ei = EI(f, mesh.vector, mesh.vector_weights, params.vector)
    ei.solve(M=50)
    test_params = -1 * rand(200).reshape((100, 2)) * (1 - 0.01)
    norms = []
    m_eim = [i for i in range(3, 50)]
    for m in m_eim:
        max_norm = float('-inf')
        for i in range(100):
            max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                                test_params[i, 1], M=m))
        norms += [max_norm]

    """
    norms_lgl = []
    for m in m_eim:
        log.info("Processing 2-d interpolation, N=75, M=%s", m)
        mesh_lgl = Mesh2D(-1, 1, 1, 25, N=75, M=m, qtype_x='lgl', qtype_y='lgl')
        evals_lgl = f(mesh_lgl.grid[:, :, 0], mesh_lgl.grid[:, :, 1])
        interp_lgl = mesh_lgl.interpolate_func(evals_lgl)

        max_norm_lgl = float('-inf')
        i = 0
        for p in test_params:
            i += 1
            lgl = np.abs(np.square(f(mesh_lgl.x, p).flatten() -
                                   interp_lgl(mesh_lgl.x, p).flatten()))
            lgl = sqrt(np.sum(mesh_lgl.w_x * lgl))
            max_norm_lgl = max(max_norm_lgl, lgl)
        norms_lgl += [max_norm_lgl]
    """

    print("N  |   EI norm     ")
    print("-------------------")
    print("5  | %e" % norms[2])
    print("10 | %e" % norms[7])
    print("15 | %e" % norms[12])
    print("20 | %e" % norms[17])
    print("25 | %e" % norms[22])
    print("30 | %e" % norms[27])
    print("35 | %e" % norms[32])
    print("40 | %e" % norms[37])
    print("45 | %e" % norms[42])
    print("50 | %e" % norms[-1])

    plt.figure("2D Example 1 L2 norms", figsize=(8, 6))
    plt.plot(m_eim, np.log10(norms), 'k-o', label='EIM')
    plt.legend(loc=0)
    plt.xlim((0, 52))
    plt.ylim((-7, 0.5))
    plt.xlabel("M")
    plt.ylabel("log_10(max(L2 norm))")
    plt.savefig("example1_2d_l2_norms.png", dpi=120, pad_inches=0)

    plt.show()
