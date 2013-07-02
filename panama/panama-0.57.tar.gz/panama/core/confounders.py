import numpy as np
import scipy as sp
import GPy
import testing
import qvalue
from GPy.util.linalg import PCA

def scaleK(K, verbose=False):
    """scale covariance K such that it explains unit variance"""
    c = sp.sum((sp.eye(len(K)) - (1.0 / len(K)) * sp.ones(K.shape)) * sp.array(K))
    scalar = (len(K) - 1) / c
    if verbose:
        print 'Kinship scaled by: %0.4f' % scalar
    K = scalar * K
    return K

def gs_cofficient(v1, v2):
    return np.dot(v2, v1) / np.dot(v1, v1)

def multiply(cofficient, v):
    return map((lambda x : x * cofficient), v)

def proj(v1, v2):
    return multiply(gs_cofficient(v1, v2) , v1)

def gs(X):
    Y = []
    for i in range(len(X)):
        temp_vec = X[i]
        for inY in Y :
            proj_vec = proj(inY, X[i])
            temp_vec = map(lambda x, y : x - y, temp_vec, proj_vec)
        Y.append(temp_vec)
    return Y

class ConfounderGPLVM(object):
    def __init__(self, expr, snps, covariates=None, population_structure=None, associations=True, interactions=False, num_factors=None, max_iterations=20, max_num_factors=30, FDR_assoc = 0.2, restarts=None):

        self.Y = expr
        self.S = snps
        self.N, self.D = expr.shape
        self.Q1 = self.S.shape[1]
        self.Y_means = self.Y.mean(axis=0)
        self.Y_stds = self.Y.std(axis=0)
        self.Y -= self.Y_means
        self.Y /= self.Y_stds
        self.S_centered = (self.S - self.S.mean(axis=0))/self.S.std(axis=0)
        self.candidate_associations = []

        self.max_num_factors = max_num_factors
        if num_factors is None:
            self.Q = self.Q_init()
            self.factors_how = 'detected'
        else:
            self.Q = num_factors
            self.factors_how = 'user-supplied'

        self.cov = covariates
        if covariates is None:
            self.num_cov = 0
        else:
            self.num_cov = covariates.shape[1]

        self.pop = population_structure
        kernel = self.kernel()

        initial_input_dim = self.Q+self.num_cov
        if self.pop is not None:
            initial_input_dim += 1

        self.model = GPy.models.GPLVM(self.Y, initial_input_dim, kernel=kernel)
        self.X = self.model.X[:, :self.Q]
        self.update_inputs()
        self.model.ensure_default_constraints()
        self.FDR_associations = FDR_assoc
        self.FDR_interactions = 0.2
        self.max_iterations = max_iterations
        self.panama_mode = associations
        self.limmi_mode = interactions
        self.restarts = restarts

        print self


    def __str__(self):
        model_str = "Model: "

        if self.panama_mode:
            model_str += "associations (PANAMA) "
        if self.panama_mode and self.limmi_mode:
            model_str += "+"
        if self.limmi_mode:
            model_str += "interactions (LIMMI)"

        model_str += "\n%d samples, %d transcripts, %d SNPs, %d latent factors (%s)" % (self.N, self.D, self.Q1, self.Q, self.factors_how)
        model_str += "\nAssociation FDR: %f, Interaction FDR: %f" % (self.FDR_associations, self.FDR_interactions)
        model_str += "\nSNPs in covariance: %d " % len(self.candidate_associations)
        model_str += "\nMaximum training iterations: %d " % self.max_iterations
        if self.cov is not None:
            model_str += "\nAccounting for %d covariates" % self.cov.shape[1]
        if self.pop is not None:
            model_str += "\nAccounting for population structure"

        return model_str + "\n\n"

    def update_inputs(self):
        ncand = len(self.candidate_associations)
        kernel = self.kernel()
        self.model.kern = kernel

        # 1. Factors
        inputs = self.X

        # 2. Covariates
        if self.num_cov != 0:
            inputs = np.concatenate((inputs, self.cov), axis=1)

        # 3. Population structure
        if self.pop is not None:
            inputs = np.concatenate((inputs, np.zeros((self.N, 1))), axis=1)

        # 4. SNPs
        inputs = np.concatenate((inputs, self.S_centered[:, self.candidate_associations]), axis=1)

        self.model.X = inputs.copy()
        self.model.input_dim = self.model.X.shape[1]
        self.model._set_params(self.model._get_params())
        self.constrain_nonlatent()


    def kernel(self):
        num_candidates = len(self.candidate_associations)
        input_dim = self.Q + num_candidates + self.num_cov

        # 1. Factors
        kernel = GPy.kern.linear(self.Q)
        kernel.parts[0].name = 'confounders'

        # 2. Covariates
        if self.cov is not None:
            kernel = GPy.kern.kern.add(kernel, GPy.kern.linear(self.num_cov, ARD=True), tensor=True)
            kernel.parts[-1].name = 'covariates'

        # 3. Population structure
        if self.pop is not None:
            if self.pop is True:
                K = scaleK(np.dot(self.S, self.S.T))
            else:
                K = self.pop

            kernel = GPy.kern.kern.add(kernel, GPy.kern.fixed(1, K), tensor=True)
            kernel.parts[-1].name = 'popstruct'
            input_dim += 1

        # 4. SNPs
        if num_candidates != 0:
            kernel = GPy.kern.kern.add(kernel, GPy.kern.linear(num_candidates, ARD=True), tensor=True)
            kernel.parts[-1].name = 'genetics'

        kernel += GPy.kern.bias(input_dim)

        return kernel

    def kernel_testing(self, genetics=True, confounders=True):
        m = self.model.copy() # FIXME: this uses a fair bit of memory
        m.unconstrain('')
        if not genetics:
            m.constrain_fixed('genetics', 0.0)
        if not confounders:
            m.constrain_fixed('confounders', 0.0)
        m.constrain_fixed('X')
        m.ensure_default_constraints()
        self.optimize(update_inputs=False)
        return m.kern.K(m.X) + np.eye(self.N) * m['noise'][0]

    def Q_init(self):
        """
        Returns the number of PCA dimensions that explain
        90% of the variance.

        """

        U, s, V = np.linalg.svd(self.Y.copy(), full_matrices = False)
        eigv = np.sort(s**2)[::-1]
        expl = np.cumsum(eigv)
        pca_dim = np.nonzero(expl/expl.max() > 0.90)[0].min()

        nf = min(self.max_num_factors, pca_dim)

        if nf == self.max_num_factors:
            print "WARNING: PCA detected a large number of latent dimensions (%d).\nWe reverted to the max_num_factors value (%d) to keep things tractable. \nIf you want, you can change the default max_num_factors value\n\n" % (pca_dim, self.max_num_factors)

        return nf

    def association_scan(self):
        print "Association scan... ",
        K = self.kernel_testing(genetics=False, confounders=True)
        pval = testing.interface(self.S_centered, self.Y, K, I = None,
                                 model='LMM', parallel=False, # TODO parallelize
                                 file_directory = None, jobs = 0)[0]
        print "[DONE]"
        # convert to qvalues
        qval = qvalue.estimate(pval)
        return qval, pval

    def interaction_scan(self):
        pass

    def get_latent(self, pca_rotation=True):
        pass

    def panama_step(self):
        X = self.model.X.copy()
        # X = np.asarray(gs(X.T)).T
        # X = np.linalg.qr(X)[0]
        X -= X.mean(axis = 0)
        X = PCA(X, X.shape[1])[0]
        X -= X.mean(axis=0)
        X /= X.std(axis=0)
        K = self.kernel_testing(genetics=False, confounders=False)
        K = scaleK(K)
        if len(self.candidate_associations) != 0:
            covs = self.S_centered[:, self.candidate_associations].copy()
        else:
            covs = None

        pv = testing.interface(self.S_centered, X[:, :self.Q], K, covs=covs, model = "LMM",
                               parallel = False, jobs = 0,
                               file_directory=None)[0] # TODO cleanup


        # Number of tests conducted
        num_tests = X.shape[1]*self.S.shape[1]*self.iteration
        qv = qvalue.estimate(pv, m=num_tests)

        # Set the qvalue of the current associations to 1
        qv[self.candidate_associations,:] = 1

        # Greedily construct addition set by adding the BEST (lowest qv) SNP for each factor
        # (if significant)
        new_candidates = []

        for i in xrange(qv.shape[1]):
            i_best = qv[:,i].argmin()
            qv_best = qv[:,i].min()
            # if significant, add it
            if qv_best<=self.FDR_associations:
                new_candidates.append(i_best)
                # and set the corrisponding qvalue to 1
                qv[i_best,:] = 1

        # Add candidates
        nc_old = len(self.candidate_associations)
        self.candidate_associations.extend(new_candidates)
        nc = len(self.candidate_associations)
        dl = nc-nc_old

        assert len(np.unique(self.candidate_associations)) == len(self.candidate_associations)

        return dl

    def constrain_nonlatent(self):
        ind = range(self.Q, self.model.input_dim)
        fixed = ""
        for i in ind:
            fixed += "|%d" % i
        self.model._set_params(self.model._get_params())
        self.model.unconstrain('')
        self.model.constrain_fixed('X_\d+_(%s)$' % fixed)
        self.model.ensure_default_constraints()

    def limmi_step(self):
        K = np.eye(self.N) #TODO # self.Kpop

        # get latent factors and rotate to PCA
        X = self.getLatent(ard_reweight = True, pca_rotation = True, rotate_varimax = False)

        inter = interaction_scan.get_candidate_interactions(self.pheno, self.snps_raw, X, K,
                                                            interactions_iter = self.interactions_iter,
                                                            pv_max_stored = self.pv_max_stored,
                                                            topn_interactions = self.topn_interactions,
                                                            FDR_addition_interactions = self.FDR_addition_interactions,
                                                            candidate_interactions = self.candidate_interactions,
                                                            parallel = self.parallelize,
                                                            Njobs = self.Njobs)

        Nint_new, candidate_interactions, int_pv_qv = inter
        self.interactions_pv, self.interactions_qv = int_pv_qv
        # how to handle new interactions?
        if self.add_inter_fixed:
            # add fixed to covariance
            for i in xrange(len(candidate_interactions)):
                i_fact = candidate_interactions[i][0]
                i_snp  = candidate_interactions[i][1]
                # create local kernel matrix
                xx = (self.snps_raw[:,i_snp]*X[:,i_fact])[:,SP.newaxis]
                xx -= xx.mean(axis=0)
                xx /= xx.std(axis=0)
                # append to covariates
                self.covariates = SP.concatenate((self.covariates,xx),axis=1)
                self.nC = self.covariates.shape[1]
        else:
            # add to dynamic covariance relearning
            # note: this has issues as the tested interactions are on rotated factors...
            self.candidate_interactions=candidate_interactions

        return Nint_new

    def optimize(self, update_inputs=True):
        success = False
        max_tries = 10
        tries = 0

        while not success:
            if update_inputs:
                self.update_inputs()

            if tries > max_tries:
                break
            if self.restarts is None:
                try:
                    self.model.optimize('bfgs', messages=0)
                except Exception:
                    self.model.randomize()
                    tries+=1
                    continue
            else:
                self.model.optimization_runs = []
                self.model.optimize_restarts(self.restarts, verbose=True, optimizer='bfgs')

            success = True


    def fit(self):
        print("Training PANAMA with an association FDR of %.2f" % self.FDR_associations)

        if self.limmi_mode:
            print("Training PANAMA with an interaction FDR of %.2f" % self.FDR_interactions)

        it = 0

        train = True
        while train and it < self.max_iterations:
            self.iteration = it + 1

            print "Iteration %d" % it
            associations_added, interactions_added = 0, 0
            if it == 0:
                print "\t Optimizing factor model... ",
                self.optimize()
                self.X = self.model.X[:, :self.Q]
                print "[DONE]"
            else:
                if self.panama_mode:
                    print "\t running PANAMA step... ",
                    associations_added = self.panama_step()
                    print "[DONE]"
                    print "\t Added %d SNPs" % associations_added

                elif associations_added == 0 and self.limmi_mode:
                    print "\t running LIMMI step... ",
                    interactions_added = self.limmi_step()
                    print "[DONE]"

                print "\t Optimizing joint model... ",
                self.optimize()
                self.X = self.model.X[:, :self.Q]
                print "[DONE]"

                if associations_added == 0 and interactions_added == 0:
                    train = False

            it += 1
