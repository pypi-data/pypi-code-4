import numpy
import numpy.linalg as la
import reikna.cluda as cluda

api = cluda.ocl_api()
platform = api.get_platforms()[0]
device = platform.get_devices()[1]
thr = api.Thread(device)

src = """
KERNEL void test(GLOBAL_MEM float *dest)
{
    const int idx = get_global_id(0);
    dest[idx] = log((idx + 1e-6) / 100.);
}
"""



prg_false = thr.compile(src, fast_math=False)
prg_true = thr.compile(src, fast_math=True)

test_false = prg_false.test
test_true = prg_true.test

N = 100
n_dev = thr.array(N, numpy.float32)

test_false(n_dev, global_size=N)
ns_false = n_dev.get()

test_true(n_dev, global_size=N)
ns_true = n_dev.get()

print ns_false.ravel()
print ns_true.ravel()
print la.norm(ns_false - ns_true) / la.norm(ns_true)

