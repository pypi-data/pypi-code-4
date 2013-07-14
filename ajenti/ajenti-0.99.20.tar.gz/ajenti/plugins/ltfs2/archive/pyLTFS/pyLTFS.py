# -*- coding: utf-8 -*-


import hashlib
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base
import sqlamp
import os
import time
import locale

#print locale.getpreferredencoding()
#print sys.stdout.encoding


class TapeLibraryHandler():

    def __init__(self):
        self.options = {}

        # after a depth of 'iMaxDepth_sqlamp' in hierarchy just dump a "tree"
        # call as text (instead of inserting each file/folder as a node to
        # the database)
        # raising this number will make the traversal a lot slower
        # leaving this in as this will build a nodegraph in the database
        # which might come in handy later
        # (what really gets easy is moving a directory or something like that)
        # (also finding the parent directories is a little easier with this)
        # but for now, speed is most important...
        # also note that the database field for the text that holds the "tree"
        # output cannot be larger than 2^32 characters, so if we have gigantic
        # trees we might run into DB-errors (in this case raising this number
        # will make individual dumps smaller thus prohibit a "too-much-data" error)
        self.options["iMaxDepth_sqlamp"] = 1

        # this will control the display depth of the call to "tree"
        # leaving this at zero will not limit the tree at all
        # a value of 5 means cutting of the "tree" at 5 hierarchy levels
        # WARNING! this will result in data not being present in the database
        # (everything below the hierarchy level wont be in there)
        # I've only put this in as a last means (speed vs. quality)
        self.options["iMaxDepth_TreeDump"] = 0

        # if we want to store/find Sonderzeichen, this is also a little costly
        # but its not so bad, better leave it on...
        # True traversing took 1860.133 ms, finding took 285.214 ms
        # (propably "tree" has to do more work)
        # False traversing took 2122.753 ms, finding took 193.997 ms
        self.options["bRespectUnicode"] = True

        # if bTreeDumpFullPaths is enabled it will store the full path
        # for each file, if it is disabled, it will only store the filename
        # plus those liny things indicating hierarchy
        #
        #    |-- LTFS_Client
        #    |   |-- 01_From
        #    |   |   `-- 2013_01_29
        #    |   |       |-- ajenti
        #    |   |       |   |-- ajenti-0.6.2-1.noarch.rpm
        #
        # storing only the filenames has pros and cons:
        # pro: less memory consumption (about 35% the size of fullpaths)
        # pro: less time spent converting unicode (very minor)
        # pro: when searching this will only return distinct hits
        #      (otherwise we'll get hits for every file in a _directory_
        #      matching the searchterm as well)
        # con: the liny hierarchy indicators seem to be different
        #      for different shells (unicode vs. ascii)
        # con: a lot! more time spent to find which the actual parent directory
        #      really is (need to parse lines above)
        #
        # for now speed is most important so leave this at 'True'
        self.options["bTreeDumpFullPaths"] = True

        # find the exact entry in a dump
        # to be precise, this will reconstruct the full path for each entry
        # this can be quite costly because we dont store the full path in the
        # database but only the form of the "tree" call
        # (filename plus indicators of hierarchy)
        # also see option "bTreeDumpFullPaths" above
        # this in turn (we could also store the fullpath in the dump)
        # is a conscience choice [this way we dont get extra search hits
        # for a file's folder plus it takes less space in the database]
        # note: to see the exact output you need a iLogLevel of at least 2
        self.options["bFindExactly"] = True

        # exclude hidden directories (while writing nodes to the databse)
        # this has no effect on the "tree" call
        self.options["bExludeHidden"] = True

        # be talkative for debugging
        # the higher this value, the more it will spit (print) out
        self.options["iLogLevel"] = 0

        # add all nodes at once (this is like 15% faster)
        self.options["bAddAll"] = True
        self.lNodes = []

    def lic_InitDB(self, sUser="syslink",
                        sPass="syslink",
                        sDBName="syslink_tapelibrary",
                        sDBType="postgresql"):

        # for SQL authentication
        # for mysql we only need a user with enough rights ("DBManager")
        # for postgresql we need to make a database by hand in advance
        sSQLUser = sUser
        sSQLPass = sPass
        sSQLDBname = sDBName

        # choice of
        # "mysql" # cannot perform test because of broken pipe bug
        # "sqlite"  # 5224.302 ms | 1624.892 ms on "/" 74MB
        # "sqlitememory"  # 3774.578 ms | 1494.738 ms on "/"
        # "postgresql"  # 6607.466 ms | 1766.244 ms on "/" ~67MB
        sDatabaseType = sDBType

        if sDatabaseType == "sqlitememory":
            engine = sqlalchemy.create_engine('sqlite:///:memory:',
                                        echo=False,
                                        convert_unicode=True,
                                        encoding='utf-8')

        elif sDatabaseType == "mysql":
            # hm, seems to be an issue with mysql and longtext here
            # on lager dumps I am getting errors of "broken pipe"
            # maybe we can stick with sqlite?
            engine = sqlalchemy.create_engine('mysql+mysqlconnector://%s:%s@localhost'
                                        % (sSQLUser, sSQLPass),
                                        echo=False,
                                        convert_unicode=False,
                                        encoding='utf-8')
            try:
                engine.execute("CREATE DATABASE IF NOT EXISTS %s" % sSQLDBname)
            except:
                pass
            engine.execute("USE %s" % sSQLDBname)  # select new db

        elif sDatabaseType == "sqlite":
            sDatabaseStorage = "/lichtwerk/01_projekte/0065_LTFS_SyslinkLTFS/LTFS_Produktion/01_ScriptsPlugins/database_storage/syslink.db"
            engine = sqlalchemy.create_engine('sqlite:///%s' % sDatabaseStorage,
                                        echo=False,
                                        convert_unicode=True,
                                        encoding='utf-8')

        elif sDatabaseType == "postgresql":
            # note: syslink has sqlalchemy 0.5.5 installed (different syntax)
            #engine = sqlalchemy.create_engine('postgres://%s:%s@localhost/%s' \
            engine = sqlalchemy.create_engine('postgresql+psycopg2://%s:%s@localhost/%s' \
                                        % (sSQLUser, sSQLPass, sSQLDBname),
                                        echo=False,
                                        convert_unicode=True,
                                        encoding='utf-8')

        metadata = sqlalchemy.MetaData(engine)

        BaseNode = declarative_base(metadata=metadata,
                                    metaclass=sqlamp.DeclarativeMeta)

        global DBContentNode
        class DBContentNode(BaseNode):
            __tablename__ = 'node'
            __mp_manager__ = 'mp'
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            parent_id = sqlalchemy.Column(sqlalchemy.ForeignKey('node.id',
                                            ondelete='CASCADE'))
            parent = sqlalchemy.orm.relation("DBContentNode", remote_side=[id])
            checksum = sqlalchemy.Column(sqlalchemy.UnicodeText())

            if sDatabaseType.find("sqlite") != -1:
                name = sqlalchemy.Column(sqlalchemy.Unicode())
                fullpath = sqlalchemy.Column(sqlalchemy.Unicode())
                treedump = sqlalchemy.Column(sqlalchemy.UnicodeText())
            if sDatabaseType.find("mysql") != -1:
                name = sqlalchemy.Column(sqlalchemy.Unicode(512))
                fullpath = sqlalchemy.Column(sqlalchemy.Unicode(512))
                treedump = sqlalchemy.Column(sqlalchemy.dialects.mysql.LONGTEXT(unicode=True))
            if sDatabaseType.find("postgresql") != -1:
                name = sqlalchemy.Column(sqlalchemy.Unicode())
                fullpath = sqlalchemy.Column(sqlalchemy.Unicode())
                treedump = sqlalchemy.Column(sqlalchemy.UnicodeText())

            def __init__(self, name='', fullpath='', parent=None, treedump='', checksum=''):
                self.name = name
                self.fullpath = fullpath
                self.parent = parent
                self.treedump
                self.checksum = checksum

            def __repr__(self):
                return '<DBContentNode %r>' % self.fullpath

        global DBContentTape
        class DBContentTape(BaseNode):
            __tablename__ = 'tape'
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            rootnode_id = sqlalchemy.Column(sqlalchemy.ForeignKey('node.id'))
            name = sqlalchemy.Column(sqlalchemy.Unicode(255))
            custom_a = sqlalchemy.Column(sqlalchemy.UnicodeText())
            custom_b = sqlalchemy.Column(sqlalchemy.UnicodeText())
            custom_c = sqlalchemy.Column(sqlalchemy.UnicodeText())
            custom_d = sqlalchemy.Column(sqlalchemy.UnicodeText())

            def __init__(self, name='', rootnode=None,
                        custom_a="",
                        custom_b="",
                        custom_c="",
                        custom_d="",):
                self.name = name
                if rootnode:
                    self.rootnode_id = rootnode.id
                self.custom_a = custom_a
                self.custom_b = custom_b
                self.custom_c = custom_c
                self.custom_d = custom_d

            def __repr__(self):
                return '<DBContentTape %r>' % self.name

        self.DBContentNode = DBContentNode
        self.DBContentTape = DBContentTape

        BaseNode.metadata.create_all(engine)
        self.session = sqlalchemy.orm.sessionmaker(engine)()

    def log(self, sString, iLevel=0):
        if iLevel <= self.options["iLogLevel"]:
            print sString

    def string_UnicodeConvert(self, sString):
        '''
        we shoud be operating on unicode everywhere (Sonderzeichen etc.)
        so to ensure we can compare strings correctly we'll have to run them
        through this function
        also: output of "tree" e.g might have different encoding...
        '''
        try:
            sString = sString.decode(locale.getpreferredencoding())
        except Exception, e:
            self.log(e, 0)

        return sString

    def lic_ConstructFullPath(self, oNode):
        '''
        note: not used anymore
        this was used in case of storing all nodes in the database via sqlamp
        we used to only store the directory name and not the full path
        so we could reconstruct the fullpath here by traversing sqlamp "ancestors"
        '''
        #print "constructing full path for %s" % oNode.name

        lAnchestors = oNode.mp.query_ancestors(and_self=True).all()
        if len(lAnchestors) == 1:
            # we have the root node
            return oNode.name
        else:
            return os.sep.join([oAnchestor.name for oAnchestor in lAnchestors])

    def lic_CheckTreeDumpStyle(self, lLines):
        '''
        on my systems, a "tree" call can have differently styled output
        sometimes it is
        "├"
        "└"
        sometimes it is
        "|--"
        "`--"
        '''
        sTokenDirect_unicode = u"├"
        sTokenDirect_ascii = "|--"

        sStyle = "unknown"
        for sLine in lLines:
            if sLine.find(sTokenDirect_unicode) != -1:
                sStyle = "unicode"
                return sStyle

            elif sLine.find(sTokenDirect_ascii) != -1:
                sStyle = "ascii"
                return sStyle

        return sStyle

    def lic_SplitTreeLine(self, sLine, sDumpStyle):
        '''
        if we dont dump the fullpath for each file (but only the filename
        plus those liny indicators of hierarchy) this function will split those
        lines into the relevant parts (sHierarchy, sFile, iLevels)
        note: this doesnt seem to use the same tokens in all shells
        sometimes this uses
        "├"
        "└"
        sometimes it uses
        "|--"
        "`--"
        '''

        if sDumpStyle == "unknown":
            return False

        sTokenDirect1_unicode = u"├"
        sTokenDirect2_unicode = u"└"
        sTokenDirect1_ascii = "|--"
        sTokenDirect2_ascii = "`--"

        iFound = sLine.find(eval('sTokenDirect1_%s' % sDumpStyle))
        if iFound == -1:
            iFound = sLine.find(eval('sTokenDirect2_%s' % sDumpStyle))
            if iFound == -1:
                self.log("ignoring line %s" % sLine, 3)

                return False

        sHierarchy = sLine[:iFound]
        sFile = sLine[iFound + 4:]
        iLevels = len(sHierarchy) / 4

        return (sHierarchy, sFile, iLevels)

    def lic_ConstructFullPathTree(self, iLineIndexOrig,
                                    iLevelsOrig,
                                    lAllLines,
                                    sResult,
                                    sDumpStyle):
        '''
        this will dig through a treedump of the form which doesnt have full paths
        but only the filenames plus those liny indicators of hierarchy
        in this case we dont know beforehand which the actual parent folder is for an entry like this

        |-- LTFS_Client
        |   |-- 01_From
        |   |   `-- 2013_01_29
        |   |       |-- ajenti
        |   |       |   |-- ajenti-0.6.2-1.noarch.rpm

        so we have to traverse upwards line by line to find a parent...

        note: the result of a "tree" call doesnt seem to use the same tokens in all shells:
        sometimes this uses
        "├"
        "└"
        sometimes it uses
        "|--"
        "`--"
        this aint good for parsing [but is respected in lic_SplitTreeLine()]

        one strategy to speed this up would be to cache this in a dictionary
        where we store already found parents [with linenumbers etc.]
        so at least we dont have to make the lookup multiple times for same entries...
        '''
        self.log("looking for parent of %s" % lAllLines[iLineIndexOrig], 2)

        bFoundParent = False
        iLineIndexParentCheck = iLineIndexOrig - 1  # we want to look upwards
        lRange = range(len(lAllLines) - 1)

        while not bFoundParent:
            if iLineIndexParentCheck in lRange:
                t = self.lic_SplitTreeLine(lAllLines[iLineIndexParentCheck],
                                            sDumpStyle)
                if t:
                    (sHierarchyCheck, sFileCheck, iLevelsCheck) = t
                    if iLevelsCheck < iLevelsOrig:
                        sResult = "%s/%s" % (sFileCheck, sResult)
                        bFoundParent = True

                        self.log("parent now %s" % sResult, 3)

                        # recursive here we go
                        sResult = self.lic_ConstructFullPathTree(
                                                        iLineIndexParentCheck,
                                                        iLevelsCheck,
                                                        lAllLines,
                                                        sResult,
                                                        sDumpStyle)
                else:
                    # we came to the top
                    bFoundParent = True

                iLineIndexParentCheck -= 1

        return sResult

    def lic_TraverseDirectory(self, oParent, iDepth, checksums={}):
        '''
        this is getting the directory contents (file- and directory names)
        recursively. please read the comments for options "iMaxDepth_sqlamp",
        "iMaxDepth_TreeDump", "bRespectUnicode" and "iMaxDepth_TreeDump"
        to see how this works internally

        TODO: broken pipe problems with mysql and large texts (> 1.000.000)
        SOLVED: by using postgresql instead :)
        '''

        # insert a simple "tree" call dump instead
        # of continueing to insert real nodes into the database
        if iDepth >= self.options["iMaxDepth_sqlamp"]:

            sOptions = ""
            if self.options["bRespectUnicode"]:
                # [is important for special character encoding...]
                sOptions = "%s -N" % sOptions
            if self.options["bTreeDumpFullPaths"]:
                # [will print fullpath prefix for each file]
                sOptions = "%s -f " % sOptions
            if self.options["iMaxDepth_TreeDump"] > 0:
                sOptions = "%s -L %s" % (sOptions,
                                        self.options["iMaxDepth_TreeDump"])

            sDump = os.popen("tree %s %s" % (sOptions, oParent.fullpath)).read()

            # this is a little costly, but have to do for Sonderzeichen...
            if self.options["bRespectUnicode"]:
                sDump = self.string_UnicodeConvert(sDump)

            oParent.treedump = sDump

            if iDepth == 0:
                # special case for root node (this has been comitted by hand)
                self.session.add(oParent)
                self.session.commit()

            return

        # if "iMaxDepth_sqlamp" is not reached > continue inserting real nodes
        # of files/folders into the database
        sParentFullPath = oParent.fullpath

        try:
            lEntries = os.listdir(sParentFullPath)
        except:
            lEntries = []
            self.log("cannot determine dirlist for %s" % sParentFullPath, 1)

        for s in lEntries:

            if s[0] == "." and self.options["bExludeHidden"]:
                continue

            # this is a bit (not much) costly, but have to do for special chars
            if self.options["bRespectUnicode"]:
                s = self.string_UnicodeConvert(s)

            # add the node
            sFullPath = os.sep.join([sParentFullPath, s])

            checksum = ''
            if len(sFullPath.split('/')) > 3:
                sPartPath = '/' + sFullPath.split('/', 3)[3]
                if sPartPath in checksums:
                    checksum = checksums[sPartPath]

            oNewNode = DBContentNode(
                name=s,
                fullpath=sFullPath,
                parent=oParent,
                checksum=checksum
            )
            self.lic_AddNode(oNewNode)

            # trverse recursevly if we find a directory
            if os.path.isdir(sFullPath):
                #print "found directory %s" % sFullPath
                self.lic_TraverseDirectory(oNewNode, iDepth + 1, checksums)

    def lic_AddNode(self, oNewNode):
        if self.options["bAddAll"]:
            self.lNodes.append(oNewNode)
        else:
            self.session.add(oNewNode)
            self.session.commit()

    def lic_CreateTape(self, sRootPath, sTapeName,
                        custom_a="",
                        custom_b="",
                        custom_c="",
                        custom_d="",
                        checksumFile=None):

        if not os.path.exists(sRootPath):
            print "rootpath doesnt exist"
            self.log("rootpath doesnt exist", 0)
            return

        '''
        # === see if everything is in place
        if self.options["sDatabaseType"] == "mysql":
            # mysql running?
            sMySQL = os.popen("ps aux").read()
            if sMySQL.find("mysqld") != -1:
                self.log("OK    mysqld seems to be running", 0)
            else:
                self.log("ERROR mysqld seems to be down", 0)
        '''

        if self.options["iLogLevel"] > 0:
            # lets do some profiling
            t1 = time.time()

        # construct a root node for this tape
        # add and commit to session by hand (because we need inserted id)
        oRoot = DBContentNode(name=sRootPath, fullpath=sRootPath)
        self.session.add(oRoot)
        self.session.commit()

        # construct a new tape
        oTape = DBContentTape(name=sTapeName, rootnode=oRoot,
                        custom_a=custom_a,
                        custom_b=custom_b,
                        custom_c=custom_c,
                        custom_d=custom_d)
        self.session.add(oTape)
        self.session.commit()

        checksums = {}
        if checksumFile:
            for l in open(checksumFile).read().splitlines():
                if l:
                    checksums['/' + l.split(' ', 2)[2]] = l.split(' ', 2)[0]

        # traverse everything below the root node
        self.lic_TraverseDirectory(oRoot, 0, checksums)

        if self.options["bAddAll"]:
            self.session.add_all(self.lNodes)
            self.session.commit()

        if self.options["iLogLevel"] > 0:
            # lets do some profiling
            t2 = time.time()
            self.log('%s took %0.3f ms' % ("traversing", (t2 - t1) * 1000.0), 1)

    def lic_getTape(self, oNode=None, sName=None):
        '''
        just get the corresponding Tape for any node in the Database (or by name)
        '''
        if sName:
            lTapes = self.session.query(DBContentTape).filter(DBContentTape.name == sName).all()
            if lTapes:
                return lTapes[0]
            else:
                return None

        oRoot = oNode.mp.query_ancestors(and_self=True).all()[0]
        try:
            oTape = self.session.query(DBContentTape).filter(
                                DBContentTape.rootnode_id == oRoot.id).one()
            return (oTape, oRoot)
        except:
            self.log("no tape found for Node %s" % oNode)
            return False

    def lic_deleteTape(self, sTapename):
        '''
        just get rid of everything in the database
        regarding this tape
        [this means the entry in "tape" table as well as
        all corresponding entries in "node" table]
        '''
        lRootNodes = []
        lTapes = self.session.query(DBContentTape).filter(
                            DBContentTape.name == sTapename).all()
        for oTape in lTapes:
            lRootNodes.extend(self.session.query(DBContentNode).filter(
                            DBContentNode.id == oTape.rootnode_id).all())
        for oTape in lTapes:
            self.session.delete(oTape)
            self.session.commit()
            print "deleting tape %s" % oTape
        for oRootNode in lRootNodes:
            self.session.delete(oRootNode)
            self.session.commit()

    def lic_FilterSearchTerm(self, sSearchTerm, bSearchContent=True, limit=10000, offset=0):
        '''
        filter the stuff in the datase according to specified searchterm
        go over all tapes, get the corresponding rootnode () and query all
        '''

        class SearchResult (object):
            pass

        class FoundNode (object):
            pass

        searchResult = SearchResult()
        searchResult.tapes = []
        searchResult.nodes = []

        if self.options["bRespectUnicode"]:
            sSearchTerm = self.string_UnicodeConvert(sSearchTerm)

        if self.options["iLogLevel"] > 0:
            t1 = time.time()

        # lookup tapes by custom fields 
        lFound = self.session.query(DBContentTape) \
                    .filter(sqlalchemy.or_(
                        DBContentTape.name.ilike('%' + sSearchTerm + '%'),
                        DBContentTape.custom_a.ilike('%' + sSearchTerm + '%'),
                        DBContentTape.custom_b.ilike('%' + sSearchTerm + '%'),
                        DBContentTape.custom_c.ilike('%' + sSearchTerm + '%'),
                        DBContentTape.custom_d.ilike('%' + sSearchTerm + '%') 
                    )) \
                    .all()
        for oTape in lFound:
            searchResult.tapes.append(oTape)

        if bSearchContent:
            # filtering the node names or their treedump beneath
            a, b = sSearchTerm, None
            op = None
            if 'AND' in sSearchTerm:
                op = sqlalchemy.and_
                a, b = sSearchTerm.split('AND', 1)
            if 'OR' in sSearchTerm:
                op = sqlalchemy.or_
                a, b = sSearchTerm.split('OR', 1)

            a = a.strip()
            if b:
                b = b.strip()

            if a.startswith('-'):
                qa = sqlalchemy.not_(DBContentNode.name.ilike('%' + a[1:] + '%'))
            else:
                qa = DBContentNode.name.ilike('%' + a + '%')

            if b:
                if b.startswith('-'):
                    qb = sqlalchemy.not_(DBContentNode.name.ilike('%' + b[1:] + '%'))
                else:
                    qb = DBContentNode.name.ilike('%' + b + '%')

            if op:
                query = op(qa, qb)
            else:
                query = qa

            query = sqlalchemy.or_(DBContentNode.checksum.ilike('%' + a + '%'), query)

            lFound = self.session.query(DBContentNode)
            lFound = lFound.filter(query)
            lFound = lFound.order_by(DBContentNode.fullpath).all()

            lFoundDump = self.session.query(DBContentNode).filter(
                        DBContentNode.treedump.ilike('%' + sSearchTerm + '%'))\
                        .all()
                        #.limit(limit).offset(offset).all()
        else:
            lFound = lFoundDump = []

        if len(lFound) > 0:
            s = "found '%s' %s time(s) (as direct Node in the database):" \
                % (sSearchTerm, len(lFound))
            self.log(s, 1)
        for oFound in lFound:
            r = self.lic_getTape(oFound)
            if not r:
                continue
            (oTape, oRoot) = r
            #s = "   [tape %s] %s" % (oTape.name, oFound.fullpath)
            #self.log(s, 1)
            searchResult.tapes.append(oTape)
            
            fn = FoundNode()
            fn.tape = oTape
            fn.path = oFound.fullpath
            fn.checksum = oFound.checksum
            
            searchResult.tapes.append(oTape)
            searchResult.nodes.append(fn)

        if len(lFoundDump) > 0:
            s = "found '%s' in treedumps of %s Nodes in the database:" \
                % (sSearchTerm, len(lFoundDump))
            self.log(s, 1)
        for oFound in lFoundDump:
            ''' paranoia check, not needed really...
            if oFound.treedump is None:
                print "hm, no treedump on %s" % oFound
                continue
            '''
            r = self.lic_getTape(oFound)
            if not r:
                continue
            (oTape, oRoot) = r
            searchResult.tapes.append(oTape)

            if self.options["bFindExactly"]:
                lLines = oFound.treedump.split('\n')[1:]
                lLinesMatch = [s for s in lLines if s.lower().find(sSearchTerm.lower()) != -1]

                # check which style the dump used for its hierarchy tokens
                # ("unicode" or "ascii", "unknown" if something went wrong)
                sDumpStyle = self.lic_CheckTreeDumpStyle(
                                        lLines[:max(len(lLines), 10)])

                s = "   [tape %s] %s time(s) in treedump beneath Node '%s':" \
                    % (oTape.name, len(lLinesMatch), oFound.fullpath)
                self.log(s, 1)
                
                for sLine in lLinesMatch:
                    iLineIndex = lLines.index(sLine)

                    if self.options["bTreeDumpFullPaths"]:
                        t = self.lic_SplitTreeLine(sLine, sDumpStyle)
                        if t:
                            (sHierarchy, sFullFile, iLevels) = t
                            fn = FoundNode()
                            fn.tape = oTape
                            fn.path = sFullFile
                            searchResult.tapes.append(oTape)
                            searchResult.nodes.append(fn)
                        else:
                            s = "      hm, someting wrong with %s ?" % sLine
                            self.log(s)

                    else:
                        # OK, this can take a loong time
                        # (not adviced to actually use this option
                        # but leaving in as reference)
                        # TODO: speed this up!
                        t = self.lic_SplitTreeLine(sLine, sDumpStyle)
                        if t:
                            (sHierarchy, sFile, iLevels) = t
                            sResult = self.lic_ConstructFullPathTree(iLineIndex,
                                                                iLevels,
                                                                lLines,
                                                                sFile,
                                                                sDumpStyle)
                            # have to append the fullpath of the root
                            # to what we found in the dump
                            sResult = "%s/%s" % (oRoot.fullpath, sResult)
                            fn = FoundNode()
                            fn.tape = oTape
                            fn.path = sResult
                            searchResult.tapes.append(oTape)
                            searchResult.nodes.append(fn)
                        else:
                            if self.options["iMaxDepth_sqlamp"] != 1:
                                s = "reached the top row %s" % sLine
                                self.log(s, 3)
            else:
                if oFound.fullpath is not None:
                    s = "  ? time(s) in treedump beneath Node '%s':" \
                        % oFound.fullpath
                    self.log(s, 1)
                    s = "    option 'bFindExactly' disabled, \
                        so being quiet here (and not waste time on finding \
                        the exact locations)..."
                    self.log(s, 1)
                else:
                    s = "hm, no fullpath on %s" % oFound
                    self.log(s, 1)

        s = "=" * 45
        self.log(s, 1)

        if self.options["iLogLevel"] > 0:
            t2 = time.time()
            s = '%s took %0.3f ms' % ("search", (t2 - t1) * 1000.0)
            self.log(s, 1)

        # make the list of tapes distinct
        searchResult.tapes = list(set(searchResult.tapes))
        searchResult.total = len(searchResult.nodes)

        newNodes = []
        nodes = sorted(searchResult.nodes, key=lambda x: x.path)

        def step(n, depth):
            nodes.remove(n)
            n.depth = depth
            newNodes.append(n)
            for node2 in nodes:
                if node2.path.startswith(n.path):
                    step(node2, depth + 1)

        for node in nodes:
            step(node, 0)

        searchResult.nodes = newNodes
        searchResult.nodes = searchResult.nodes[offset:offset+limit]

        # Chop off mountpoint
        for node in searchResult.nodes:
            if node.path.startswith('/'):
                s = node.path.split('/', 3)
                if len(s) > 3:
                    node.path = '/' + s[3]
                node.filepath = node.path
                node.filepath2 = node.path
                node.filepath3 = node.path

        return searchResult
