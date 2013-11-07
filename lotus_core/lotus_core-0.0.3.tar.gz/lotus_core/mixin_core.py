
import lotus_core_hpp
import read_basis_DATA

class Env_mol:
  def __init__(self):
    self.eri           = lotus_core_hpp.ERI_incore()
    self.max_diis      = 6
    self.max_scf       = 100
    self.threshold_scf = 1.0e-6
    self.functor       = lotus_core_hpp.HF_Functor()

  def use_file(self):
    self.eri     = lotus_core_hpp.ERI_file()

  def use_direct(self):
    self.eri     = lotus_core_hpp.ERI_direct()

  def use_incore(self):
    self.eri     = lotus_core_hpp.ERI_incore()


class Mixin_core_py:

  def __init__(self):
    self.env_mol=Env_mol()

  def show_env_mol(self):
    print "   env_mol.max_diis,max_scf: ", self.env_mol.max_diis, self.env_mol.max_scf 
    print "   env_mol.eri ", type(self.env_mol.eri) 
    self.env_mol.eri.show()
    print "   env_mol.functor: ", type(self.env_mol.functor) 


  def cal_Fock_sub_py(self,retM, D):
    self.cal_Fock_sub(retM, D, self.env_mol.eri, self.env_mol.functor)

  def cal_Fock_sub_u_py(self,retMa, retMb, Da, Db):
    self.cal_Fock_sub_u(retMa, retMb, Da, Db, self.env_mol.eri, self.env_mol.functor)


  def get_mix_dens_core(self, max_d):
    return 1.0

  def get_Matrix_py(self):
    return lotus_core_hpp.dMatrix()

  def get_vector_int(self):
    N_cgtos = self.get_N_cgtos()
    return lotus_core_hpp.get_vector_int(N_cgtos)

  def get_vector_double(self):
    N_cgtos = self.get_N_cgtos()
    return lotus_core_hpp.get_vector_double(N_cgtos)

  def get_vector_Matrix_py(self, N):
    return lotus_core_hpp.get_vector_dMatrix(N)

  def mix_D_matrix(self, D, ind, pre_ind, mix_dens):
    tmpM = self.get_Matrix_py()
    lotus_core_hpp.mat_mul(D[ind], mix_dens, D[ind])
    lotus_core_hpp.mat_mul(tmpM, (1.0-mix_dens), D[pre_ind])
    lotus_core_hpp.mat_add(D[ind], tmpM, D[ind])

  def do_diis(self, F, D, S, E, n_scf, max_diis):
    self.diis(F, D, S, n_scf, max_diis) 
 
  def cal_force_py(self):
    spin = self.moldata.spin
    if spin==1:
      return self.cal_force_r(self.env_mol.functor) 
    else:
      return self.cal_force_u(self.env_mol.functor) 


  def cal_force_r_py(self):
    return self.cal_force_r(self.env_mol.functor) 

  def cal_force_u_py(self):
    return self.cal_force_r(self.env_mol.functor) 


  def scf_py(self):
    spin = self.moldata.spin
    if spin==1:
      return self.r_scf_py() 
    else:
      return self.u_scf_py() 


  def r_scf_py(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print " ===== r_scf_py ====="
    N_cgtos  = self.get_N_cgtos()
    max_diis = self.env_mol.max_diis
    D = self.get_vector_Matrix_py(max_diis)
    F = self.get_vector_Matrix_py(max_diis)
    E = []
    for i in range(max_diis):
      D[i].set_IJ(N_cgtos, N_cgtos)
      F[i].set_IJ(N_cgtos, N_cgtos)
      E.append(0.0)

    occ = lotus_core_hpp.Util.cal_occ(self.moldata.scgtos, self.moldata.ecps, self.moldata.mol_charge, 1)
    lotus_core_hpp.Util.cal_D(D[max_diis-1], self.X_a, occ)
    self.prepare_eri(self.env_mol.eri)
    self.cal_Fock_sub_py(F[0], D[max_diis-1]) 

    H_core = self.get_Matrix_py()
    S      = self.get_Matrix_py()
    self.cal_matrix("H_core", H_core)
    self.cal_matrix("S",      S)
    lotus_core_hpp.mat_add(F[0], H_core, F[0])

    max_d   = 10
    max_scf = self.env_mol.max_scf
    for n_scf in range(max_scf):
      ind     = n_scf%max_diis
      pre_ind = (n_scf+max_diis-1)%max_diis
      if process_num==0:
        print " ----- r_scf_py n_scf=",n_scf," ind,pre_ind ",ind,pre_ind," -----"

      lotus_core_hpp.cal_eigen(F[ind], S, self.X_a, self.lamda_a)
      lotus_core_hpp.Util.cal_D(D[ind], self.X_a, occ)

      mix_dens = self.get_mix_dens_core(max_d)
      self.mix_D_matrix(D, ind, pre_ind, mix_dens) 
      self.cal_Fock_sub_py(F[ind], D[ind])
      lotus_core_hpp.mat_add(F[ind], F[ind], H_core)
      E[ind] = self.cal_show_energy(D[ind], H_core, self.moldata)
      self.ene_total=E[ind]

      max_d = lotus_core_hpp.Util.get_max_d(D, ind, pre_ind)
      if process_num==0:
        print "    mix_dens, max_d ", mix_dens, max_d
      if n_scf>0 and max_d<self.env_mol.threshold_scf:
        break 
      if n_scf==max_scf-1:
        print " ******************* CAUTION !! *******************"
        print " dose not convegy in scf_loop, max_diis=", max_diis 
        print " **************************************************"
      self.do_diis(F, D, S, E, n_scf, max_diis)
    


  def u_scf_py(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print " ===== u_scf_py ====="
    N_cgtos  = self.get_N_cgtos()
    max_diis = self.env_mol.max_diis
    Da = lotus_core_hpp.get_vector_Matrix_py(max_diis)
    Db = lotus_core_hpp.get_vector_Matrix_py(max_diis)
    Fa = lotus_core_hpp.get_vector_Matrix_py(max_diis)
    Fb = lotus_core_hpp.get_vector_Matrix_py(max_diis)
    E = []
    for i in range(max_diis):
      Da[i].set_IJ(N_cgtos, N_cgtos)
      Db[i].set_IJ(N_cgtos, N_cgtos)
      Fa[i].set_IJ(N_cgtos, N_cgtos)
      Fb[i].set_IJ(N_cgtos, N_cgtos)
      E.append(0.0)

    occ_a = lotus_core_hpp.get_vector_double(N_cgtos)
    occ_b = lotus_core_hpp.get_vector_double(N_cgtos)
    lotus_core_hpp.Util.cal_occ_ab(occ_a, occ_b, self.moldata.scgtos, self.moldata.ecps,
                               self.moldata.mol_charge, self.moldata.spin)
    lotus_core_hpp.Util.cal_D(Da[max_diis-1], self.X_a, occ_a)
    lotus_core_hpp.Util.cal_D(Db[max_diis-1], self.X_b, occ_b)
    self.prepare_eri(self.env_mol.eri)
    self.cal_Fock_sub_u_py(Fa[0], Fb[0], Da[max_diis-1], Db[max_diis-1]) 

    H_core = lotus_core_hpp.get_Matrix_py()
    S      = lotus_core_hpp.get_Matrix_py()
    self.cal_matrix("H_core", H_core)
    self.cal_matrix("S",      S)
    lotus_core_hpp.mat_add(Fa[0], H_core, Fa[0])
    lotus_core_hpp.mat_add(Fb[0], H_core, Fb[0])

    max_d   = 10
    max_scf = self.env_mol.max_scf
    for n_scf in range(max_scf):
      ind     = n_scf%max_diis
      pre_ind = (n_scf+max_diis-1)%max_diis
      if process_num==0:
        print " ----- u_scf_py n_scf=",n_scf," ind,pre_ind ",ind,pre_ind," -----"

      lotus_core_hpp.cal_eigen(Fa[ind], S, self.X_a, self.lamda_a)
      lotus_core_hpp.cal_eigen(Fb[ind], S, self.X_b, self.lamda_b)
      lotus_core_hpp.Util.cal_D(Da[ind], self.X_a, occ_a)
      lotus_core_hpp.Util.cal_D(Db[ind], self.X_b, occ_b)

      mix_dens = self.get_mix_dens_core(max_d)
      self.mix_D_matrix(Da, ind, pre_ind, mix_dens) 
      self.mix_D_matrix(Db, ind, pre_ind, mix_dens) 
      self.cal_Fock_sub_py(Fa[ind], Da[ind])
      self.cal_Fock_sub_py(Fb[ind], Db[ind])
      lotus_core_hpp.mat_add(Fa[ind], Fa[ind], H_core)
      lotus_core_hpp.mat_add(Fb[ind], Fb[ind], H_core)
      E[ind] = self.cal_show_energy_u(Da[ind], Db[ind], H_core, self.moldata)
      self.ene_total=E[ind]

      max_d_a = lotus_core_hpp.Util.get_max_d(Da, ind, pre_ind)
      max_d_b = lotus_core_hpp.Util.get_max_d(Db, ind, pre_ind)
      max_d   = max_d_a
      if max_d<max_d_b:
        max_d=max_d_b
      if process_num==0:
        print "    mix_dens, max_d_a,b ", mix_dens, max_d_a,max_d_b," max_d ",max_d
      if n_scf>0 and max_d<self.env_mol.threshold_scf:
        break 
      if n_scf==max_scf-1:
        print " ******************* CAUTION !! *******************"
        print " dose not convegy in scf_loop, max_diis=", max_diis 
        print " **************************************************"

      self.do_diis(Fa, Da, S, E, n_scf, max_diis)
      self.do_diis(Fb, Db, S, E, n_scf, max_diis)

  def get_functor(self, sel):
    ret_functor = lotus_core_hpp.HF_Functor() 
    if   sel ==None:      return lotus_core_hpp.HF_Functor() 
    elif sel =="hf":      return lotus_core_hpp.HF_Functor()
    elif sel =="slater":  return lotus_core_hpp.Slater_Functor()
    elif sel =="svwn":    return lotus_core_hpp.SVWN_Functor()
    elif sel =="b88":     return lotus_core_hpp.B88_Functor()
    elif sel =="blyp":    return lotus_core_hpp.BLYP_Functor()
    elif sel =="b3lyp":   return lotus_core_hpp.B3LYP_Functor()
    else:
      print ' ERROR!!   The functionr or methodi,"',ssl,'" is not implemented yet. '
      quit()


  def set_data_for_mixin_core(self, instring):
    caldata = {"spin":1, "charge":0, "method":"hf", "basis":None}
    instring2 = lotus_core_hpp.Util_MPI.broadcast_text(instring)
    lines = instring2.split("\n")
    for li in lines:
      ws=li.split()
      if len(ws)!=0:
        if ws[0]=="use_direct:":
          self.env_mol.use_direct()
        if ws[0]=="use_file:":
          self.env_mol.use_file()
        if ws[0]=="use_incore:":
          self.env_mol.use_incore()
        if ws[0]=="spin:":
          caldata["spin"]   = int(ws[1]) 
        if ws[0]=="charge:":
          caldata["charge"] = int(ws[1]) 
        if ws[0]=="method:":
          caldata["method"] = ws[1].lower()
        if ws[0]=="basis:":
          process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
          basis_name = ws[1]
          qm_string_root=""
          if process_num==0:
            basis_lines    = read_basis_DATA.ReadInput.get_lines_from_basis_file(basis_name.lower())
            str_info       = read_basis_DATA.ReadInput.read_str_info_from_instring(instring)
            atoms          = str_info.atoms
            scgtos         = read_basis_DATA.ReadInput.get_scgtos_from_lines(str_info, basis_lines)
            ecps           = read_basis_DATA.ReadInput.get_ecps_from_lines(str_info, basis_lines)
            qm_string_root = read_basis_DATA.ReadInput.get_qm_string(atoms, scgtos, ecps)
          qm_string  = lotus_core_hpp.Util_MPI.broadcast_text( qm_string_root )
          caldata["basis"]=qm_string
    #
    self.moldata.set_basis_from_string(caldata["basis"])
    self.moldata.mol_charge = caldata["charge"]
    self.moldata.spin       = caldata["spin"]
    self.env_mol.functor = self.get_functor(caldata["method"])


  def read_in_string(self, instring):
    self.set_data_for_mixin_core(instring)


  def read_in_file(self, infile):
    import os
    instring1 = ""
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    error_flag=0
    if os.path.isfile(infile)==True and process_num==0: 
      instring1 = open(infile).read()
    else:
       if process_num==0:
         print "  ERROR!! cannot open file: ",infile
         error_flag=1
    error_flag = lotus_core_hpp.Util_MPI.broadcast_int(error_flag)
    if error_flag==1: quit(1)
    instring2 = lotus_core_hpp.Util_MPI.broadcast_text(instring1)
    self.read_in_string(instring2)


  def debug_show_type_matrix(self):
    print type(self.get_Matrix_py())

  def show_core_py(self, no=0):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print "========== lotus_core ======="
      print "  ///// ENV_MOL /////"
      print "   mol_charge ",self.moldata.mol_charge," spin ",self.moldata.spin
      N_scgtos = self.get_N_scgtos()
      N_ecps   = self.get_N_ecps()
      self.show_env_mol()
      print "  ///// SCGTOS, N_scgtos=",N_scgtos," /////"
      for i in range(N_scgtos):
        pass
        print "   ----- scgtos i=",i," -----"
        self.moldata.scgtos[i].show()
      print "  ///// ECPS, N_ecps=",N_ecps," /////"
      for i in range(N_ecps):
        print "   ----- ecps i=",i," -----"
        self.moldata.ecps[i].show()

  
class Lotus_core_py_dMatrix(lotus_core_hpp.Lotus_core, Mixin_core_py):
  def __init__(self):
    lotus_core_hpp.Lotus_core.__init__(self)
    Mixin_core_py.__init__(self)
  def read_in_string(self, instring):
    self.set_data_for_mixin_core(instring)
  def show(self):
    self.show_core_py()


class Lotus_core_py_dMatrix_map(lotus_core_hpp.Lotus_core_map, Mixin_core_py):
  def __init__(self):
    lotus_core_hpp.Lotus_core_map.__init__(self)
    Mixin_core_py.__init__(self)
  def read_in_string(self, instring):
    self.set_data_for_mixin_core(instring)
  def show(self):
    self.show_core_py()
  def get_Matrix_py(self):
   return lotus_core_hpp.dMatrix_map()
  def get_vector_Matrix_py(self, N):
   return lotus_core_hpp.get_vector_dMatrix_map(N)


def create_lotus(sel="dMatrix"):
  if   sel=="dMatrix":      return Lotus_core_py_dMatrix()
  elif sel=="dMatrix_map":  return Lotus_core_py_dMatrix_map()



if __name__ == '__main__':
  pass


