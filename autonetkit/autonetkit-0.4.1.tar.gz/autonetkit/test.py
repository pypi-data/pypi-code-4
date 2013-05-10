from autonetkit import console_script

#console_script.main()

import autonetkit
autonetkit.update_http()

import autonetkit.load.graphml as graphml
import autonetkit.anm

anm =  autonetkit.ANM()
#input_graph = graphml.load_graphml("small_internet.graphml")
input_graph = graphml.load_graphml("example/singleas.graphml")
g_in = anm.initialise_graph(input_graph)
autonetkit.update_http(anm)
