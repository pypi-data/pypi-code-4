print 'checking %s repositories' % rql('Any COUNT(X) WHERE X is Repository')[0][0]

rset = rql('Any R1, R2 WHERE R1 changeset RC, R2 changeset RC, NOT R1 identity R2,  R1 created_by U, NOT R2 created_by U')
if rset:
    print 'duplicated revisions', rset

rset = rql('Any VC,VC2 WHERE VC content_for VF, VC from_revision R, VC2 content_for VF, VC2 from_revision R, VC eid VCE, VC2 eid > VCE')
if rset:
    print 'file referenced several time by a revision using from_revision relation', rset

rset = rql('Any F,R,RR GROUPBY F,R,RR WHERE VC at_revision R, VC content_for F, R revision RR HAVING COUNT(VC) > 1')
if rset:
    print 'file referenced several time by a revision using at_revision relation', rset

print 'merge nodes', rql('Any R GROUPBY R WHERE R parent_revision X HAVING count(X) > 1')
print 'branching nodes', rql('Any X GROUPBY X WHERE R parent_revision X HAVING count(R) > 1')

