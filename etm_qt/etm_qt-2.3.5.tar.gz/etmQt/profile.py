import pstats
p = pstats.Stats('etm.prof')
p.sort_stats('cumulative').print_stats(20)
# p.print_stats(20)