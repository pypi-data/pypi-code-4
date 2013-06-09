import inspect
import re

re_re   = re.compile("\:re\:")
re_type = re.compile("\:ty\:")

# ----------------------------------------------------------- results handling

def result(success, given, xpmtl, msg, *args, **kwargs):
    res = {}
    reason = None
    if len(args) > 0:
        reason = args[0]
    # get filename, line num, stuff. should always want the -2nd frame in the stack, since -1 is the exec().
    frame = inspect.getouterframes(inspect.currentframe())[-2]
    # frame, filename, linenum, function_name, lines, index
    if "file" in kwargs:
        res["file"]  = kwargs["file"]
    else:
        res["file"]  = frame[1]
    res["line"]  = frame[2]
    res["pass"]  = success
    res["msg"]  = msg
    res["comp"] = []
    res["comp"].append(subresult(xpmtl, given, reason))
    return res

def subresult(xpmtl, given, reason):
    sres = {}
    sres["xpect"]  = given
    sres["got"]    = xpmtl
    sres["reason"] = reason
    return sres

# ---------------------------------------------------------------- comparisons

def comp(self, xpmtl, given, msg, invert):
    if re_re.match(str(given)):
        return re_match(xpmtl, given, msg, invert)
    else:
        return is_eq(xpmtl, given, msg, invert)

def is_eq(xpmtl, given, msg, invert):
    if (xpmtl == given and invert == False) or (xpmtl != given and invert == True):
        return True, None
    else:
        return False, None

def re_match(xpmtl, given, msg, invert):
    restr = given[4:]
    if re.search(restr, str(xpmtl)):
        return True, None
    else:
        if invert:
            return True, None
        else:
            return False, "regexp failure ('got' is not a match for 'expected')"


def deepcomp(self, xpmtl, given, msg, invert):
    # just a helper function which resets states, hashes the structs to be compared, then calls _compare()
    self.nodestack = []
    self.xhash = {}
    hash(self, xpmtl, self.xhash)
    self.nodestack = []
    self.ghash = {}
    hash(self, given, self.ghash)
    compare(self, msg, invert)

def hash(self, element, hashdict):
    # FIXME see if this can be rewritten without self
    if isinstance(element, (tuple, list, dict)):
        # composites are handled here
        if isinstance(element, (dict,)):
            # for dicts we push a 'd' onto the stack for "dict",then push each dict key onto the stack and call
            # ourselves on that key's value
            self.nodestack.append('d')
            for key in sorted(element.keys(), key=lambda key: str(key)):
                self.nodestack.append(str(key))
                hash(self, element[key], hashdict)
                self.nodestack.pop()
        else:
            # lists and tuples are handled like dicts, but get 'l' or 't' on the stack
            if isinstance(element, (list,)):
                self.nodestack.append('l')
            else:
                self.nodestack.append('t')
            for idx, subelem in enumerate(element):
                self.nodestack.append(str(idx))
                hash(self, subelem, hashdict)
                self.nodestack.pop()
        self.nodestack.pop()
    else:
        # leafnodes (scalar values) handled here
        key = ".".join(self.nodestack)
        hashdict[key] = element

def compare(self, msg, invert):
    # FIXME see if this can be rewritten without self
    if invert:
        # for an inverted test, our only failure condition is equality. a single mismatch is enough to declare
        # success and return.
        mismatch = inv_compare(self, self.xhash, self.ghash)
        if not mismatch:
            mismatch = inv_compare(self, self.ghash, self.xhash)
        if not mismatch:
            self.results.append(result(False, None, None, msg, "structs were identical"))
        self.results.append(result(True, None, None, msg, None))
        return

    # normal compares are more complex.
    failed = False
    failkeys = []
    for key in sorted(self.xhash.keys()):
        # see if the current key has any of failkeys[] as a prefix. if so, we do not want to proceed; we'll
        # just be producing mismatch cascade errors
        fkmatch = False
        for fk in failkeys:
            if re.match(fk, key): fkmatch = True
        if fkmatch: continue
        # actual comparison starts here
        if key not in self.ghash:
            # key mismatch results in adding a mismatch condition to this test's result. the tests for 'failed'
            # let us know whether we're adding the FIRST mismatch or not. only compares have this tracking
            res = "node {} (value '{}') only in experimental struct".format(key, self.xhash[key])
            if failed:
                self.results[-1]["comp"].append(subresult(None, None, res))
            else:
                failed = True
                failkeys.append(key[:-2]) # key mismatch; add (most of) key to failkeys[]
                self.results.append(result(False, None, None, msg, res))
        else:
            # if the key exists in xhash + ghash, call _test_scalar() to see if they are eqivalent
            passed, reason = comp(self, self.ghash[key], self.xhash[key], None, False)
            if not passed:
                res = "node {} values don't match".format(key)
                if failed:
                    self.results[-1]["comp"].append(subresult(self.ghash[key], self.xhash[key], res))
                else:
                    failed = True
                    self.results.append(result(False, self.ghash[key], self.xhash[key], msg, res))
    # normal compare, step 2: repeat key comparison with ghash as the source. there's no need to check scalars
    # because we've already tested everything which is in both structs.
    failkeys = []
    for key in sorted(self.ghash.keys()):
        fkmatch = False
        for fk in failkeys:
            if re.match(fk, key): fkmatch = True
        if fkmatch: continue
        if key not in self.xhash:
            res = "node {} (value '{}') only in given struct".format(key, self.ghash[key])
            if failed:
                self.results[-1]["comp"].append(subresult(None, None, res))
            else:
                failed = True
                failkeys.append(key[:-2])
                self.results.append(result(False, None, None, msg, res))
    # finally, if failed still isn't True, then the compare is a pass
    if not failed:
        self.results.append(result(True, None, None, msg, None))

def inv_compare(self, a, b):
    # FIXME only requires self because comp() needs it
    for key in sorted(a.keys()):
        if key not in b:
            return True
        else:
            passed, reason = comp(self, a[key], b[key], None, False)
            if not passed: return True
    return False
