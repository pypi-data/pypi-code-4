import hddm
data, params = hddm.generate.gen_rand_data(size=200)
m = hddm.HDDM(data)
m.sample(5000, burn=20)
x, y, ql, qh = hddm.utils.plot_posterior_quantiles(m, hexbin=True)
