# Description: Reliability estimation
# Category:    evaluation
# Uses:        prostate
# Referenced:  Orange.evaluation.reliability
# Classes:     Orange.evaluation.reliability.Learner

import Orange
prostate = Orange.data.Table("prostate.tab")

knn = Orange.classification.knn.kNNLearner()
reliability = Orange.evaluation.reliability.Learner(knn)

res = Orange.evaluation.testing.cross_validation([reliability], prostate)

reliability_res = Orange.evaluation.reliability.get_pearson_r(res)

print
print "Estimate               r       p"
for estimate in reliability_res:
    print "%-21s%7.3f %7.3f" % (Orange.evaluation.reliability.METHOD_NAME[estimate[3]],
                                 estimate[0], estimate[1])

reliability = Orange.evaluation.reliability.Learner(knn, estimators=[Orange.evaluation.reliability.SensitivityAnalysis()])

res = Orange.evaluation.testing.cross_validation([reliability], prostate)

reliability_res = Orange.evaluation.reliability.get_pearson_r(res)

print
print "Estimate               r       p"
for estimate in reliability_res:
    print "%-21s%7.3f %7.3f" % (Orange.evaluation.reliability.METHOD_NAME[estimate[3]],
                                 estimate[0], estimate[1])

indices = Orange.data.sample.SubsetIndices2(prostate, p0=0.7)
train = prostate.select(indices, 0)
test = prostate.select(indices, 1)

reliability = Orange.evaluation.reliability.Learner(knn, estimators=[Orange.evaluation.reliability.ICV()])
reliabilityc = reliability(train)
res = Orange.evaluation.testing.test_on_data([reliabilityc], train, test)

METHOD_NAME = Orange.evaluation.reliability.METHOD_NAME

print
print "Method used in internal cross-validation: ", METHOD_NAME[reliabilityc.estimation_classifiers[0].chosen[0]]

top5 = sorted((abs(result.probabilities[0].reliability_estimate[0].estimate), id) for id, result in enumerate(res.results))[:5]
for estimate, id in top5:
    print "%7.3f %i" % (estimate, id)
