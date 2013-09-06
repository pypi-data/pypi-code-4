import sys
import os
from pancake.sf import SharedFeature

def get_gv(pangenome, chroms, starts, stops, all_flag, region_flag, max_entries, max_nodes, max_edges, output):
	#all_flag: include all genomes
	#region_flag: only show FIs covering given region

	#PREPARATION
	color_dic = {}
	sf_ind, fi_ind = 1,1
	all_chroms = list(pangenome.chromosomes.keys())
	starts_and_stops = {}
	for i in range(len(all_chroms)):
		color_dic[all_chroms[i]] = i * 1/len(all_chroms)*0.5 + 0.05 * 1/len(all_chroms)
	str_dic = dict() #will contain string representation of SFs
	tmp_sfs = dict() # will contain truncated SFs if all_flag unset
	for i in range(len(chroms)): 
		starts_and_stops[chroms[i]] = (starts[i], stops[i])

	#GET SFS and STRING REPRESENTATION 
	for i in range(len(chroms)):
		fi = pangenome.crossing_fi(chroms[i], starts[i])
		if fi.sh_feat and fi.sh_feat not in tmp_sfs:
			if all_flag:
				tmp_sfs[fi.sh_feat] = fi.sh_feat
			else:
				#get dummy SF conatining exclusively FIs appearing in output
				tmp_sfs[fi.sh_feat] = truncate_sf(fi.sh_feat, starts_and_stops, region_flag) 
			sf= tmp_sfs[fi.sh_feat]
			if len(sf) > max_entries:
				str_dic[sf] = 'SF{} [label="{}", shape=rectangle, style=filled, fillcolor="{}"];'.format(sf_ind, long_sf_str(sf), get_sf_color(fi.sh_feat, color_dic))
			else:
				str_dic[sf] = 'SF{} [label="{}", shape=rectangle, style=filled, fillcolor="{}"];'.format(sf_ind, short_sf_str(sf), get_sf_color(fi.sh_feat, color_dic))
			sf_ind+=1 #index for DOT file
		elif not fi.sh_feat:
			str_dic[fi] = 'FI{} [style=filled, label="{}", fillcolor="{} 0.3 0.85"];'.format(fi_ind, gv_str(fi), color_dic[fi.chrom])
			fi_ind+=1 #index for DOT file
		while fi.nextFI and fi.nextFI.start <= stops[i]:
			fi=fi.nextFI
			if fi.sh_feat and fi.sh_feat not in tmp_sfs:
				if all_flag:
					tmp_sfs[fi.sh_feat] = fi.sh_feat
				else:
					tmp_sfs[fi.sh_feat] = truncate_sf(fi.sh_feat, starts_and_stops, region_flag)
				sf= tmp_sfs[fi.sh_feat]
				if len(sf) > max_entries:
					str_dic[sf] = 'SF{} [label="{}", shape=rectangle, style=filled, fillcolor="{}"];'.format(sf_ind, long_sf_str(sf), get_sf_color(fi.sh_feat, color_dic))
				else:
					str_dic[sf] = 'SF{} [label="{}", shape=rectangle, style=filled, fillcolor="{}"];'.format(sf_ind, short_sf_str(sf), get_sf_color(fi.sh_feat, color_dic))
				sf_ind+=1 #index for DOT file
			elif not fi.sh_feat:
				str_dic[fi] = 'FI{} [style=filled, label="{}", fillcolor="{} 0.3 0.85"];'.format(fi_ind, gv_str(fi), color_dic[fi.chrom])
				fi_ind+=1 #index for DOT file

	#check max_nodes
	nnodes = len(str_dic)
	if nnodes>max_nodes: raise ValueError('Number of nodes in resulting graph {} > MAX_NODES {} ...ABORTING'.format(nnodes, max_nodes))

	#GET EDGES
	edge_dict = dict()
	edge_dict['others'] = set()
	for node in str_dic:
		if type(node) == SharedFeature:
			sf=node
			for entry in node:
				if entry.chrom in chroms and entry.chrom not in edge_dict: edge_dict[entry.chrom] = set()
				if entry.nextFI in str_dic:
					#SF to FI
					if entry.chrom in chroms:
						if not (entry.start > starts_and_stops[entry.chrom][1] or entry.stop < starts_and_stops[entry.chrom][0]):
							#colored edge
							edge_dict[entry.chrom].add('\"{}\" -> \"{}\" [penwidth=8 color= "{} 0.3 0.85"];'.format(str_dic[sf].split()[0], str_dic[entry.nextFI].split()[0], color_dic[entry.chrom]))
						else:
							edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[sf].split()[0], str_dic[entry.nextFI].split()[0]))
					else:
						edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[sf].split()[0], str_dic[entry.nextFI].split()[0]))
				elif entry.nextFI and entry.nextFI.sh_feat in tmp_sfs:
					#SF to SF
					next_sf = tmp_sfs[entry.nextFI.sh_feat]
					if entry.chrom in chroms:
						if not (entry.start > starts_and_stops[entry.chrom][1] or entry.stop < starts_and_stops[entry.chrom][0]):
							#colored edge
							edge_dict[entry.chrom].add('\"{}\" -> \"{}\" [penwidth=8 color= "{} 0.3 0.85"];'.format(str_dic[sf].split()[0], str_dic[next_sf].split()[0], color_dic[entry.chrom]))
						else:
							edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[sf].split()[0], str_dic[next_sf].split()[0]))
					else:
						edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[sf].split()[0], str_dic[next_sf].split()[0]))
		else:
			#FI
			fi = node
			if fi.chrom in chroms and fi.chrom not in edge_dict: edge_dict[fi.chrom] = set()
			if fi.nextFI in str_dic:
				pass
				#should never be the case
			elif fi.nextFI and fi.nextFI.sh_feat in tmp_sfs:
				next_sf = tmp_sfs[fi.nextFI.sh_feat]
				if fi.chrom in chroms:
					if not (fi.start > starts_and_stops[fi.chrom][1] or fi.stop < starts_and_stops[fi.chrom][0]):
						#colored edge
						edge_dict[fi.chrom].add('\"{}\" -> \"{}\" [penwidth=8 color= "{} 0.3 0.85"];'.format(str_dic[fi].split()[0], str_dic[next_sf].split()[0], color_dic[fi.chrom]))
					else:
						edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[fi].split()[0], str_dic[next_sf].split()[0]))
				else:
					edge_dict['others'].add('\"{}\" -> \"{}\"'.format(str_dic[fi].split()[0], str_dic[next_sf].split()[0]))



	#check max_edges
	nedges = 0
	for key in edge_dict:
		nedges+= len(edge_dict[key])
	if nedges>max_edges: raise ValueError('Number of edges in resulting graph {} > MAX_EDGES {} ...ABORTING'.format(nedges, max_edges))
	
	sys.stderr.write('...resulting graph consists of {} nodes and {} edges\n#\n'.format(nnodes, nedges))
	if not output:
		#print to STDOUT
		print('digraph G {')
		print('graph [fontsize=100 labelloc="t" label="" splines=true overlap=false];\nratio = auto;\n') # rankdir = "TB"
		for key in str_dic:
			print(str_dic[key])
			str_dic[key] = str_dic[key].split()[0]
		for key in edge_dict:
			if key == 'others':
				for edge in edge_dict[key]:
					print(edge + ' [color="0.56 0.15 0.83"];')
			else:
				for edge in edge_dict[key]:
					print(edge)
		print('}')
	else:
		#write to file
		dir, f = os.path.split(output)
		if dir:
			try:
				os.stat(dir)
			except:
				os.mkdir(dir)
		with open(output, 'wt') as dot_file:
			dot_file.write('digraph G {\n')
			dot_file.write('graph [fontsize=100 labelloc="t" label="" splines=true overlap=false];\nratio = auto;\n\n') # rankdir = "TB"
			for key in str_dic:
				dot_file.write(str_dic[key]+'\n')
				str_dic[key] = str_dic[key].split()[0]
			for key in edge_dict:
				if key == 'others':
					for edge in edge_dict[key]:
						#dot_file.write(edge + ' [color="0.56 0.15 0.83"];\n')
						dot_file.write(edge + ' [color="0 0 0.7"];\n')
				else:
					for edge in edge_dict[key]:
						dot_file.write(edge + '\n')
			dot_file.write('}\n')
		sys.stderr.write('...written to DOT file {}\n'.format(output))


def truncate_sf(sf, starts_and_stops, region_flag):
	#all_flag unset 
	new_sf = SharedFeature(sf.seq)
	entry_count, entry_dic = 0, {}
	for entry in sf.entries:
		if entry.chrom in starts_and_stops:
			if not region_flag:
				new_sf.add(entry)
			elif not (entry.start > starts_and_stops[entry.chrom][1] or entry.stop < starts_and_stops[entry.chrom][0]):
				new_sf.add(entry)
	return new_sf


def long_sf_str(sf):
	sf_dict = dict()
	s = sf.seq if len(sf.seq)<=10 else sf.seq[:5] + '...' + sf.seq[-5:]
	s += ' \({}bp\)\\n'.format(len(sf.seq))
	for entry in sf.entries:
		genome = entry.chrom.genome
		if genome not in sf_dict:
			sf_dict[genome] = dict()
		if entry.chrom not in sf_dict[genome]:
			sf_dict[genome][entry.chrom] = 1
		else: sf_dict[genome][entry.chrom] +=1
	for genome in sf_dict:
		s+= 'Genome ' + genome + ':\\n'
		for c in sf_dict[genome]:
			s+= ' ' + str(sf_dict[genome][c]) + 'x ' + str(c) + '\\n'
	return s


def short_sf_str(sf):
	sf_dict = dict()
	s = sf.seq if len(sf.seq)<=10 else sf.seq[:5] + '...' + sf.seq[-5:]
	s += ' \({}bp\)\\n'.format(len(sf.seq))
	for entry in sorted(sf.entries, key=keyfunc):
		s += '{} {}-{} '.format(entry.chrom, entry.start, entry.stop)
		s+= '-' if entry.seq.reverse else '+'
		s+= ' ({}bp)\\n'.format(entry.stop-entry.start+1)
	return s


def gv_str(node, starts_and_stops=None, all_flag=False, max_entries=500):
	s=''
	if type(node) == SharedFeature:
		s += node.seq if len(node.seq)<=10 else node.seq[:5] + '...' + node.seq[-5:]
		s += ' \({}bp\)\\n'.format(len(node.seq))
		entry_count, entry_dic = 0, {}
		for entry in sorted(node.entries, key=keyfunc):
			if entry.chrom not in entry_dic: entry_dic[entry.chrom] = []
			entry_dic[entry.chrom].append(entry)
		for chrom in entry_dic:
			for entry in entry_dic[chrom]:
				s += '{} {}-{} '.format(entry.chrom, entry.start, entry.stop)
				s+= '-' if entry.seq.reverse else '+'
				s+= ' ({}bp)\\n'.format(entry.stop-entry.start+1)
	else:
		s += '{} {}-{} '.format(node.chrom, node.start, node.stop)
		s+= '+ \({}bp\)\\n'.format(node.stop-node.start+1)
	return s


def keyfunc(x):
	return (x.chrom.name, x.start)


def get_sf_color(sf, color_dic):
	color_set=set()
	for f in sf.entries:
		color_set.add(color_dic[f.chrom])
	if len(color_set)>1:
		return "{} 0.6 0.85".format(sum(color_set)/len(color_set) + len(color_set)*0.04)#*min(color_set))
	else:
		return "{} 0.3 0.85".format(list(color_set)[0])

