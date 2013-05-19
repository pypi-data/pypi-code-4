
from numpy import array
import commpy.channelcoding.Trellis as tt
memory = array([2])
g_matrix = array([[05, 07]]) # G(D) = [1+D^2, 1+D+D^2]
trellis = tt(memory, g_matrix)
print trellis.k
print trellis.n
print trellis.total_memory
print trellis.number_states
print trellis.number_inputs
print trellis.next_state_table
print trellis.output_table
