"""
Ax_FuzzyTourney - tournament runner.

Main public entrypoint for running tournaments.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from __future__ import print_function

import sys


# ----------------------------------------------------------------------------


class RunContext(object):
    """
    Private context used by Runner during tournament execution.
    Also held by RunStatusCallback object for callback handlers to access.
    """
    def __init__(self):
        self.tournament = None # tournament config component
        self.entrants = None   # full list of entrants
        self.entrant_num = 0   # 1-based index into entrant list
        self.entrant = None    # entrant currently processing
        self.entrant_criteria = None  # criteria for current entrant
        self.entrant_lens_data = {}   # cached lens data for current entrant
        self.app_context = None  # For passing info from larger app to internals


# ----------------------------------------------------------------------------


class RunStatusCallback(object):
    """
    Wrapper for callbacks used by Runner to inform caller of status.
    Caller may subclass to define their own handlers.
    Default is NOOP on all callbacks.
    """
    def __init__(self):
        self.ctx = None  # will contain current RunContext
    def stage(self, msg):
        """Report a major update of the execution stage."""
        pass
    def entrant(self):
        """Report for each entrant as it begins to be processed."""
        pass
    def debug(self, msg):
        """Report verbose detailed debug information."""
        pass
    def is_debug(self):
        """Return False to avoid some pointless string formatting when debug() is NOOP."""
        return False


class RunStatusCallback_NOOP(RunStatusCallback):
    """
    NOOP impl of RunStatusCallback that does nothing.
    """
    pass


class RunStatusCallback_Basic(RunStatusCallback):
    def stage(self, msg):
        """Report a major update of the execution stage."""
        self._print("[AXFT][STAGE] --------------------------------------")
        self._print("[AXFT][STAGE] {0}".format(msg))
        self._print("[AXFT][STAGE] --------------------------------------")
    def entrant(self):
        """Report for each entrant as it begins to be processed."""
        self._print("[AXFT][Entrant] #{0}/{1}: {2}".format(
            self.ctx.entrant_num, len(self.ctx.entrants), self.ctx.entrant))
    def debug(self, msg):
        """Report verbose detailed debug information."""
        pass
    def is_debug(self):
        """Return False to avoid some pointless string formatting when debug() is NOOP."""
        return False
    def _print(self, msg):
        print(msg, file=sys.stderr)


class RunStatusCallback_BasicDebug(RunStatusCallback_Basic):
    def debug(self, msg):
        self._print("[AXFT][dbg] {0}".format(msg))
    def is_debug(self):
        """Return False to avoid some pointless string formatting when debug() is NOOP."""
        return True


# ----------------------------------------------------------------------------


class Runner(object):
    """
    Controller to execute actual tournament.
    Consturct and call run(tournament).
    """
    def __init__(self):
        self._ctx = RunContext()
        self.set_status_callback_handler(RunStatusCallback_NOOP())

    def set_status_callback_handler(self, run_status_callback):
        """Set new RunStatusCallback object to handle status updates."""
        if run_status_callback is None:
            run_status_callback = RunStatusCallback_NOOP()
        self._status = run_status_callback
        self._status.ctx = self._ctx
        
    def set_app_context(self, app_context):
        """
        Set new app context opaque obj, for communicating between app and internals.
        Useful for e.g. config information used by custom function extensions.
        """
        self._ctx.app_context = app_context
        
    def run(self, tournament):
        """Main tournament execution entry point."""
        self._ctx.tournament = tournament
        self._status.stage(u"Running tournament: {0}".format(tournament.name))
        self._load_entrants()
        self._setup_fields()
        self._open_select_output()
        self._process_entrants()
        self._close_select_output()
        self._status.stage(u"Done")
    
    # ----- Private -----
    
    @property
    def t(self):
        """Shorthand for tournament config stored in context."""
        return self._ctx.tournament

    def _load_entrants(self):
        """Load entrants data as specified by input config."""
        self._status.stage(u"Loading entrants ({0})".format(self.t.input.function_id))
        self._ctx.entrants = self.t.input.function.read_entrants()
        self._status.stage(u"Loaded {0} entrants".format(len(self._ctx.entrants)))
        if self._status.is_debug():
            self._status.debug(u"Entrants: ")
            self._status.debug(repr(self._ctx.entrants))
            
    def _setup_fields(self):
        """Set up output fields as specified by output field config."""
        self._status.stage(u"Setting up fields")
        field_cnt = 0
        for field in self.t.output.fields:
            field.function.setup(self.t, self._ctx.entrants)
            field_cnt += len(field.function.ids())
        self._status.stage(u"Set up {0} fields".format(field_cnt))
        if self._status.is_debug():
            self._status.debug(u"Fields: ")
            self._status.debug(u"  function_ids: {0}".format([f.function_id for f in self.t.output.fields]))
            self._status.debug(u"     field ids: {0}".format([f.function.ids() for f in self.t.output.fields]))
            self._status.debug(u"   field names: {0}".format([f.function.names() for f in self.t.output.fields]))
    
    def _open_select_output(self):
        """Open select (wrapping output) as specified by select/output config."""
        self._status.stage(u"Output ({0}) wrapped in selector".format(self.t.output.function_id))
        self._status.stage(u"Opening selector ({0})".format(self.t.select.function_id))
        self.t.select.function.open(self.t, self._ctx.entrants)

    def _close_select_output(self):
        """Close select (wrapping output) as specified by select/output config."""
        self._status.stage(u"Closing selector")
        self.t.select.function.close()
    
    def _process_entrants(self):
        """Process all the entrants. This is the main workload of the tournament execution."""
        self._status.stage(u"Processing entrants")
        self._ctx.entrant_num = 0
        for entrant in self._ctx.entrants:
            self._ctx.entrant_num += 1
            self._ctx.entrant = entrant
            self._status.entrant()
            self._process_entrant()
    
    def _process_entrant(self):
        """Process a single entrant (run judges)."""
        
        # Init criteria:
        self._ctx.entrant_criteria = dict((c.id, c.init) for c in self.t.criteria.criteria)

        # Init lens data:
        self._ctx.entrant_lens_data = {}
        
        # Run judges:
        for cfgjudge in self.t.judges.judges:
            self._run_judge(cfgjudge)

        # Give processed entrant to selector:
        self.t.select.function.entrant(self._ctx.entrant_num, self._ctx.entrant, 
            self._ctx.entrant_criteria, self._ctx.entrant_lens_data)

    def _run_judge(self, cfgjudge):
        """Run a single judge against current entrant."""
        self._status.debug(u"E> Judge '{0}'...".format(cfgjudge.name))
        for cfgheuristic in cfgjudge.heuristics:
            self._run_judge_heuristic(cfgjudge, cfgheuristic)

    def _run_judge_heuristic(self, cfgjudge, cfgheuristic):
        """Run a single heuristic for a judge against current entrant."""
        self._status.debug(u"E>J> Heuristic '{0}' on criterion '{1}'...".format(cfgheuristic.name, cfgheuristic.criterion_id))
        
        # Lens, map, reduce:
        vals = self._apply_heuristic_lens(cfgheuristic)
        vals = self._apply_heuristic_maps(cfgheuristic, vals)
        rval = self._apply_heuristic_reducer(cfgheuristic, vals)
        rval = self._apply_heuristic_reduced_maps(cfgheuristic, rval)

        # Apply to criteria:
        rval = self._apply_heuristic_to_criteria(cfgheuristic, rval)
        
    def _apply_heuristic_lens(self, cfgheuristic):
        """
        Apply specified heuristic lens on current entrant to get list of vals.
        If lens id is specified, then values of previous lenses with same id
        applied to same entrant will be re-used.
        """
        lens = cfgheuristic.lens
        vals = None
        if lens.id is not None:
            vals = self._ctx.entrant_lens_data.get(lens.id, None)
        if vals is not None:
            self._status.debug(u"E>J>H> Lens (cached #{0}) '{1}' vals: {2}".format(lens.id, lens.function_id, vals))
        else:
            vals = lens.function.execute(self._ctx.entrant)
            self._status.debug(u"E>J>H> Lens (calculated #{0}) '{1}' vals: {2}".format(lens.id, lens.function_id, vals))
        if lens.id is not None:
            self._ctx.entrant_lens_data[lens.id] = vals
        return vals

    def _apply_heuristic_maps(self, cfgheuristic, vals):
        """
        Apply specified heuristic maps in sequence on lens vals,
        returning new list of mapped vals of same length.
        """
        for map in cfgheuristic.maps:
            vals = [map.function.execute(v) for v in vals]
            self._status.debug(u"E>J>H> Mapped '{0}': {1}".format(map.function_id, vals))
        return vals

    def _apply_heuristic_reducer(self, cfgheuristic, vals):
        """
        Apply specified heuristic reducer function on mapped vals,
        returning new single value.
        """
        rval = cfgheuristic.reduce.function.execute(vals)
        self._status.debug(u"E>J>H> Reduced '{0}': {1}".format(cfgheuristic.reduce.function_id, rval))
        return rval

    def _apply_heuristic_reduced_maps(self, cfgheuristic, rval):
        """
        Apply specified heuristic reduced maps in sequence on reduced val
        (actually list containing only reduced val, since maps require list).
        Return new final reduced val.
        """
        vals = [rval]
        for map in cfgheuristic.reduced_maps:
            vals = [map.function.execute(v) for v in vals]
            self._status.debug(u"E>J>H> RMapped '{0}': {1}".format(map.function_id, vals))
        return vals[0]

    def _apply_heuristic_to_criteria(self, cfgheuristic, rval):
        """
        Apply finally lensed/mapped/reduced value to specified criteria.
        """
        if cfgheuristic.criterion_id is not None:
            self._ctx.entrant_criteria[cfgheuristic.criterion_id] += rval
            self._status.debug(u"E>J>H> Criteria '{0}' now = {1}".format(cfgheuristic.criterion_id, self._ctx.entrant_criteria[cfgheuristic.criterion_id]))
        else:
            self._status.debug(u"E>J>H> Criteria (null)")


