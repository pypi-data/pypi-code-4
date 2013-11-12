

import os
import sys
import copy



class In_Scgto:
  def __init__(self):
    self.atom_no    = None
    self.atom_kind  = None
    self.Rxyz       = None
    self.shell_type = None 
    self.num_pgto   = 0
    self.g = []
    self.d = []

  def show(self):
    print "   ----- Scgto ",self.shell_type,self.num_pgto,"  ----"
    for i in range(self.num_pgto):
      print "      i=",i," g, d ", self.g[i], self.d[i]

  def show2(self):
    print "     ----- Scgto: atom_kind ",self.atom_kind,"atom_no",self.atom_no,
    print " Rxyz ",self.Rxyz[0],self.Rxyz[1],self.Rxyz[2]
    print "      shell_type, num_pgto ", self.shell_type, self.num_pgto,"  ----"
    for i in range(self.num_pgto):
      print "        i=",i," g, d ", self.g[i], self.d[i]


class IN_ECP:
  def __init__(self):
    self.atom_no    = None
    self.atom_kind  = None 
    self.Rxyz       = None 
    self.shell_type = None 
    self.core_ele   = 0
    self.num_pecp   = 0
    self.g          = []
    self.k          = []
    self.d          = []

  def show(self):
    print "  ----- IN_ECP  shell_type, core_ele, num_pecp ",self.shell_type,core_ele,self.num_pecp," -----"
    for i in range(self.num_pecp):
      print "      i=",i," g, ,k, d ", self.g[i],"  ", self.k[i],"  ", self.d[i]

  def show2(self):
    print "  ----- IN_ECP: atom_kind ",self.atom_kind,"atom_no",self.atom_no,
    print " Rxyz ",self.Rxyz[0],self.Rxyz[1],self.Rxyz[2]
    print "    shell_type, num_pecp,core_ele ",self.shell_type, self.num_pecp, self.core_ele
    for i in range(self.num_pecp):
      print "      i=",i," g, ,k, d ", self.g[i],"  ", self.k[i],"  ", self.d[i]



class ReadInput:

  class Str_info:
    def __init__(self):
      self.atoms=[]

    def get_nth_atom_kind(self,nth):
      return copy.deepcopy(self.atoms[nth][0])

    def get_nth_Rxyz(self,nth):
      ret = []
      ret.append(self.atoms[nth][1])
      ret.append(self.atoms[nth][2])
      ret.append(self.atoms[nth][3])
      return ret

    def show(self):
      print self.atoms
      for i in range( len(self.atoms) ):
        Rxyz = self.get_nth_Rxyz(i)
        print "   Atom[",i,"]:  atom_kind ",self.get_nth_atom_kind(i),"  Rxyz  ",Rxyz[0],Rxyz[1],Rxyz[2] 
  

  @staticmethod
  def read_str_info_from_instring(instring):
    ret_str_info = ReadInput.Str_info()
    a_to_au = 1.889725989 
    lines = instring.lower().split("\n")
    for li in lines:
      ws = li.split()
      if len(ws)!=0:
        if ws[0].lower()=="atom:":
          a_data = []
          a_data.append(ws[1])
          a_data.append( float(ws[2])*a_to_au )
          a_data.append( float(ws[3])*a_to_au )
          a_data.append( float(ws[4])*a_to_au )
          ret_str_info.atoms.append(a_data)
    return ret_str_info


  @staticmethod
  def read_str_info_from_infile(filename):
    instring = ""
    if os.path.isfile(filename)==True:  instring = open(filename).read()
    return read_str_info_from_instring(instring)



  @staticmethod
  def read_keyvalue_from_instring(key,instring):
    ret=None
    lines = instring.lower().split("\n")
    for li in lines:
      ws = li.split()
      if len(ws)!=0:
        if ws[0].lower()==key:
          ret=ws[1]
          return ret


  @staticmethod
  def get_lines_from_basis_file(basis_name):
    filename_bare = basis_name + ".basis"
    if os.path.isfile(filename_bare)==True:  btext = open(filename_bare).read()
    #
    filename_cwd = os.getcwd() + "/" + basis_name + ".basis"
    if os.path.isfile(filename_cwd)==True:  btext = open(filename_cwd).read()
    #
    filename_basis_DATA = os.path.dirname(__file__) + "/basis_DATA/" + basis_name + ".basis"
    if os.path.isfile(filename_basis_DATA)==True:  btext = open(filename_basis_DATA).read()
    # 
    return btext.lower().split("\n")


  @staticmethod
  def get_basis_lines_for_atom(sel_atom, basis_lines):
    i = 0
    for li in basis_lines:
      words     = li.split()
      pre_words = []
      if i!=0: pre_words = basis_lines[i-1].split()
      if len(words)!=0 and len(pre_words)!=0:
        if words[0] == sel_atom.lower() and pre_words[0] == "****":
          ret_lines = []
          j=0
          while len(basis_lines[i+j].split())!=0:
            ws = basis_lines[i+j].split()
            if ws[0]=="****":  return ret_lines
            else:              ret_lines.append(basis_lines[i+j])
            j=j+1
          return ret_lines
      i=i+1

  @staticmethod
  def get_ecp_lines_for_atom(sel_atom, basis_lines):
    sel_ecp = sel_atom.lower() + "-ecp"
    it = iter(basis_lines)
    ret_lines = []
    for li in it:
      words = li.split()
      if len(words)!=0:
        if words[0].lower()==sel_ecp:
          ret_lines.append(li)

          for li2 in it:
            if li2.lower().find("ecp")==-1:
              ret_lines.append(li2)
            else:
              del ret_lines[ len(ret_lines)-1 ]
              return ret_lines 


  class BasisData:
    def __init__(self):
      self.atom   = None
      self.scgtos = []

    def show(self):
      print "----- BasisData ",self.atom,len(self.scgtos),"-----"
      for i in range(len(self.scgtos)):
        print "   ///// i=",i,"//////"
        self.scgtos[i].show()


  class ECP_DATA:
    def __init__(self):
      self.atom_kind   = None 
      self.ecps        = []
      self.num_ecps    = 0
      self.core_ele    = 0

    def show(self):
      print "----- ECP_DATA ",self.atom_kind,len(self.ecps),"-----"
      for i in range(len(self.ecps)):
        print "   ///// i=",i,"//////"
        self.ecps[i].show()      

  @staticmethod 
  def shell_type2int(st):
    if st=="s":  return 0
    if st=="p":  return 1
    if st=="d":  return 2
    if st=="f":  return 3
    if st=="g":  return 4
    if st=="h":  return 5
    if st=="i":  return 6


  @staticmethod
  def get_atom_basis_data_from_lines(basis_lines):
    it = iter(basis_lines)


    words = it.next().split()
    ret_basis_data= ReadInput.BasisData()
    ret_basis_data.atom = words[0]
    for li in it:
      words = li.split()
      if words[0]=="sp":
        data_s = In_Scgto()
        data_p = In_Scgto()
        data_s.shell_type=ReadInput.shell_type2int("s")
        data_p.shell_type=ReadInput.shell_type2int("p")
        data_s.num_pgto = int(words[1])
        data_p.num_pgto = int(words[1])
        for j in range( int(words[1]) ):
          li = it.next()
          w_gd = li.split()
          data_s.g.append( float(w_gd[0]) )
          data_s.d.append( float(w_gd[1]) )
          data_p.g.append( float(w_gd[0]) )
          data_p.d.append( float(w_gd[2]) )
        ret_basis_data.scgtos.append(data_s)
        ret_basis_data.scgtos.append(data_p)
      else:
        data = In_Scgto()
        data.shell_type = ReadInput.shell_type2int(words[0])
        data.num_pgto   = int(words[1])
        for j in range( int(words[1]) ):
          li = it.next()
          w_gd = li.split()
          data.g.append( float(w_gd[0]) )
          data.d.append( float(w_gd[1]) )
        ret_basis_data.scgtos.append(data)
    return ret_basis_data    

  @staticmethod
  def get_ecp_shell_type(string):
    if string.find("-")==-1:
      return -1
    if string.find("s-")==0:
      return 0
    if string.find("p-")==0:
      return 1
    if string.find("d-")==0:
      return 2
    if string.find("f-")==0:
      return 3
    if string.find("g-")==0:
      return 4
    if string.find("h-")==0:
      return 5
    if string.find("i-")==0:
      return 6
    

  @staticmethod
  def get_atom_ecp_data_from_lines(sel_atom, ecp_lines):
    it = iter(ecp_lines)
    ret_ecp_data = ReadInput.ECP_DATA()
    ret_ecp_data.atom_kind = sel_atom
    words = it.next().split()
    ret_ecp_data.num_ecps = int(words[1])
    core_ele = int(words[2])
    flag_ecp_L = 0

    for li in it:
      ecp = IN_ECP()
      ecp.core_ele = core_ele
      words = li.split()
      if flag_ecp_L==0:
        ecp.shell_type = -1
        flag_ecp_L=1
      else:
        ecp.shell_type = ReadInput.get_ecp_shell_type(words[0])
      ecp.num_pecp   = int(it.next().split()[0])
      for i in range( ecp.num_pecp ):
        ws_kgd = it.next().split()
        ecp.k.append( float(ws_kgd[0]) )
        ecp.d.append( float(ws_kgd[1]) )
        ecp.g.append( float(ws_kgd[2]) )
      ret_ecp_data.ecps.append(ecp)
    return ret_ecp_data


  @staticmethod
  def get_atom_basis(atom_name, blines):
    alines = ReadInput.get_basis_lines_for_atom(atom_name, blines)
    if alines!=None:
      return ReadInput.get_atom_basis_data_from_lines(alines)  
    else:
      print " cannot find atom,",atom_name," in basis file "


  @staticmethod
  def get_atom_ecp(atom_name, blines):
    ecp_lines = ReadInput.get_ecp_lines_for_atom(atom_name, blines)
    if ecp_lines!=None:
      return ReadInput.get_atom_ecp_data_from_lines(atom_name, ecp_lines)
    else:
      ecp_data = []
      return ecp_data
    


  @staticmethod
  def get_scgtos_from_lines(str_info, blines):
    set_atoms = set([])
    for li_atm in str_info.atoms:
      set_atoms.add(li_atm[0])
    #
    dic_basis = {}
    for atm in set_atoms:
      abasis = ReadInput.get_atom_basis(atm, blines)
      dic_basis[atm] = abasis
    #
    ret_scgtos = []
    for i in range( len(str_info.atoms) ):
      atm        = str_info.get_nth_atom_kind(i)
      Rxyz       = str_info.get_nth_Rxyz(i)
      #
      basis_data = dic_basis[atm]
      for j in range( len(basis_data.scgtos) ): 
        scgto           = copy.deepcopy( basis_data.scgtos[j] )
        scgto.atom_no   = i
        scgto.atom_kind = atm 
        scgto.Rxyz      = Rxyz
        ret_scgtos.append(scgto)
      
    return ret_scgtos


  @staticmethod
  def get_ecps_from_lines(str_info, blines):
    set_atoms = set([])
    for li_atm in str_info.atoms:
      set_atoms.add(li_atm[0])
    #
    dic_ecp = {}
    for atm in set_atoms:
      aecp           = ReadInput.get_atom_ecp(atm, blines)
      dic_ecp[atm]   = aecp
    #
    ret_ecps = []
    for i in range( len(str_info.atoms) ):
      atm        = str_info.get_nth_atom_kind(i)
      Rxyz       = str_info.get_nth_Rxyz(i)
      #
      ecp_data   = dic_ecp[atm]
      if ecp_data!=[]:
        for j in range( len(ecp_data.ecps) ): 
          ecp            = copy.deepcopy( ecp_data.ecps[j] )
          ecp.atom_no    = i
          ecp.atom_kind  = atm
          ecp.Rxyz       = Rxyz 
          ret_ecps.append(ecp)
    return ret_ecps




  @staticmethod 
  def get_atom_Z(atom_kind):
    map_Z = { "h":1,                                                                                                                                 "he":2,
             "li":3, "be":4,                                                                                  "b":5,  "c":6,  "n":7,  "o":8,  "f":9, "ne":10,
             "na":11,"mg":12,                                                                                "al":13,"si":14, "p":15, "s":16,"cl":17,"ar":18,
              "k":19,"ca":20,"sc":21,"ti":22, "v":23,"cr":24,"mn":25,"fe":26,"co":27,"ni":28,"cu":29,"zn":30,"ga":31,"ge":32,"as":33,"se":34,"br":35,"kr":36,
             "rb":37,"sr":38, "y":29,"zr":40,"nb":41,"mo":42,"tc":43,"ru":44,"rh":45,"pd":46,"ag":47,"cd":48,"in":49,"sn":50,"sb":51,"te":52, "i":53,"xe":54,
             "cs":55,"ba":56,        "hf":72,"ta":73, "w":74,"re":75,"os":76,"ir":77,"pt":78,"au":79,"hg":80,"ti":81,"pb":82,"bi":83,"po":84,"at":85,"rn":86,
             "fr":87,"ra":88,        "rf":104,"db":105,"sg":106,"bh":107,"hs":108,"mt":109,"ds":110,

             "la":57,"ce":58,"pr":59,"nd":60,"pm":61,"sm":62,"eu":63,"gd":64,"tb":65,"dy":66,"ho":67,"er":68,"tm":69,"yb":70,"lu":71,
             "ac":89,"th":90,"pa":91, "u":92,"np":93,"pu":94,"am":95,"cm":96,"bk":97,"cf":98,"es":99,"fm":100,"md":101,"no":102,"lr":103
            }   
    return map_Z[ atom_kind.lower() ]
 
 

  @staticmethod
  def get_qm_string(atoms, scgtos, ecps=[]):
    N_scgtos = len(scgtos)
    N_ecps   = 0
    N_atoms  = scgtos[N_scgtos-1].atom_no+1
    if ecps!=[]:
      N_ecps = len(ecps)
    #
    ret_string = ""
    ret_string += "__________LOTUS_MOLECULE_INPUT_FILE__________\n\n"
    ret_string += "N_scgtos__N_ecps_N_atoms\n"
    ret_string += str(N_scgtos) + "  " + str(N_ecps) + "  " + str(N_atoms) + "\n\n"
    #
    ret_string += "__________MOLECULAR_COORDINATE_________\n"
    for i in range(len(atoms)):
      atom_kind = atoms[i][0].lower()
      x = atoms[i][1]
      y = atoms[i][2]
      z = atoms[i][3]
      atom_z = ReadInput.get_atom_Z(atom_kind)
      ret_string += "%4s  %4d  atom_z  %4d   xyz  %15f  %15f  %15f \n" % (atom_kind,atom_z,i,x,y,z)
    ret_string += "\n"
    
    ret_string += "__________SCGTOS_DATA__________\n"
    for i in range(N_scgtos):
      atom_kind = atoms[scgtos[i].atom_no][0].lower()
      atom_z    = ReadInput.get_atom_Z(atom_kind)
      x         = scgtos[i].Rxyz[0] 
      y         = scgtos[i].Rxyz[1] 
      z         = scgtos[i].Rxyz[2] 
      ret_string += "scgto: no " + str(i) + " shell_type " + str(scgtos[i].shell_type) + " atom_no " + str(scgtos[i].atom_no)
      ret_string += " atom_kind " + str(atom_kind) + " atom_z " + str(atom_z) + "   xyz   "+str(x)+"  "+str(y)+"  "+str(z)+"\n"
      ret_string += str(scgtos[i].num_pgto) + "\n"
      for j in range(scgtos[i].num_pgto):
        ret_string += "   %15f   %15f  \n" % (scgtos[i].g[j],scgtos[i].d[j])
    ret_string += "\n"
    # 
    ret_string += "__________ECP_DATA__________\n"
    for i in range(N_ecps):
      atom_no    = ecps[i].atom_no
      core_ele   = ecps[i].core_ele
      shell_type = ecps[i].shell_type
      atom_kind  = atoms[atom_no][0].lower()
      atom_z     = ReadInput.get_atom_Z(atom_kind)
      x          = ecps[i].Rxyz[0]
      y          = ecps[i].Rxyz[1]
      z          = ecps[i].Rxyz[2]
      ret_string += "ecps: no "+str(i)+" core_ele "+str(core_ele)+" shell_type "+str(shell_type)+" atom_no "+str(atom_no)
      ret_string += " atom_kind "+atom_kind+" atom_z "+str(atom_z)+"    xyz   "+str(x)+"  "+str(y)+"  "+str(z)+"\n"
      ret_string += str(ecps[i].num_pecp) + "\n"
      for j in range(ecps[i].num_pecp):
        ret_string += "  %15f  %4d  %15f " % (ecps[i].g[j], ecps[i].k[j], ecps[i].d[j]) + "\n"
    ret_string += "\n"
     
    return ret_string 

  @staticmethod 
  def get_qm_string_from_infile(infile):
    basis_name     = ReadInput.read_keyvalue_from_infile("basis:",    infile)
    basis_lines    = ReadInput.get_lines_from_basis_file(basis_name)
    str_info       = ReadInput.read_str_info_from_infile(infile)
    atoms     = str_info.atoms
    scgtos    = ReadInput.get_scgtos_from_lines(str_info, basis_lines)
    ecps      = ReadInput.get_ecps_from_lines(str_info, basis_lines)
    return ReadInput.get_qm_string(atoms, scgtos, ecps)   
 


