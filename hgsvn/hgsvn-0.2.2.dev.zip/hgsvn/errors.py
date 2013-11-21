
"""
Exception sub-hierarchy:

RuntimeError
 +-- ExternalCommandFailed
 +-- CommitCancelled
 +-- HgSVNError
      +-- UnsupportedSVNFeature
      |    +-- OverwrittenSVNBranch
      |    +-- UnsupportedSVNAction
      +-- SVNOutputError
           +-- EmptySVNLog

"""

class ExternalCommandFailed(RuntimeError):
    """
    An external command failed.
    """

class RunCommandError(ExternalCommandFailed):
    msg_prefix = ""
    returncode = 0
    cmd_string = ""
    err_msg = ""
    out_msg = ""
    
    def __init__(self, amsg, areturncode, acmd_string="", aerr_msg="", aout_msg=""):
        self.msg_prefix = amsg
        self.returncode = areturncode
        self.cmd_string = acmd_string
        self.err_msg = aerr_msg
        self.out_msg = aout_msg
        #ExternalCommandFailed.__init(self, msg() );
    
    def msg(self, noout = False):
        use_outmsg = ""
        if not noout:
            use_outmsg = self.out_msg;
        return ("%s (return code %d): %s\n%s\n%s\n"
                % (self.msg_prefix, self.returncode, self.cmd_string, self.err_msg, use_outmsg))
    
    def __str__(self):
        return self.msg()
    
    
class HgSVNError(RuntimeError):
    """
    A generic hgsvn error.
    """

class UnsupportedSVNFeature(HgSVNError):
    """
    An unsuppported SVN (mis)feature.
    """

class OverwrittenSVNBranch(UnsupportedSVNFeature):
    """
    The current SVN branch was overwritten with another one.
    """

class UnsupportedSVNAction(UnsupportedSVNFeature):
    """
    An unknown/unsupported SVN action in an SVN log entry.
    """

class SVNOutputError(HgSVNError):
    """
    A generic error with the output of an SVN command.
    """

class EmptySVNLog(SVNOutputError):
    """
    An empty SVN log entry.
    """
