__all__ = ["ChooserException", "flow", "T3Chart", "Solver"]

class ModelCheckEscape(Exception):
    pass

class ChooserException(Exception):
    pass

class Chooser(object):
    def __init__(self, chosen, stack):
        self._chosen = chosen
        self._stack  = stack
        self._it     = iter(chosen)

    def choose(self, choices):
        if choices == bool:
            choices = [True, False]
        try:
            choice = self._it.next()
            if choice not in choices:
                raise ChooserException("Program is not deterministic")
            return choice
        except StopIteration:
            self._stack+=[self._chosen + [choice] for choice in choices]
            raise ModelCheckEscape()


def check(func, chooser = Chooser):
    stack = [[]]
    while len(stack) > 0:
        chosen = stack.pop()
        try:
            func(chooser(chosen, stack))
        except ModelCheckEscape:
            pass


def flow(f):
    '''
    Decorator used to annotate methods of a T3Chart which keep a single ``chooser`` argument
    and return a dictionary of local variables of the method supposed they have assignments ::

        m: chooser -> dict

    The decorator adds the return value of the decorated method to the assignments of the
    defining T3Chart object.
    '''
    def call(self, chooser):
        res = f(self, chooser)
        if isinstance(res, list):
            self.assignments.extend(res)
        elif isinstance(res, dict):
            del res["chooser"]
            del res["self"]
            self.assignments.append(res)
        else:
            raise RuntimeError("Function must return locals()")
    call.__name__ = f.__name__
    call.__doc__  = f.__doc__
    call.flow = True
    return call

class Solver(object):
    def __init__(self, assignments):
        self.assignments  = assignments
        self.dependent    = []

    def solve(self, **client_assignments):
        return self._solve(client_assignments, set())

    def fetch(self, varname):
        return set(asgn[varname] for asgn in self.assignments if varname in asgn)

    def _solve(self, client_assignments, visited):
        '''
        The solver algorithm reduces the number of overall assignments using constraints
        imposed by client assignments.
        '''
        solution = Solver([])
        varnames = set(client_assignments.keys())
        independent = []
        for asgn in self.assignments:
            for name, value in client_assignments.items():
                # check if client assignment value fits that of a given assignment
                # if not, cancel the assignment
                if name in asgn and asgn[name] != value:
                    break
            else:
                if not set(asgn.keys()) & varnames:
                    independent.append(asgn)
                else:
                    solution.dependent.append(asgn)
        visited.update(varnames)
        F = {}
        for asgn in solution.dependent:
            for key, val in asgn.items():
                S = F.get(key,set())
                S.add(val)
                F[key] = S

        next = dict((key, val.pop()) for (key, val) in F.items()
                                     if key not in visited and
                                        len(val) == 1)
        solution.assignments = solution.dependent + independent
        solution.dependent += [S for S in self.dependent if S in independent]
        if next:
            return solution._solve(next, visited)
        else:
            return solution

class T3Chart(object):
    def __init__(self):
        self.names = set()
        self.assignments = []

    def create(self):
        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, "flow"):
                check(attr)
        self.solver = Solver(self.assignments)
        for asgn in self.assignments:
            self.names.update(asgn.keys())

    def __len__(self):
        return len(self.assignments)

    def __nonzero__(self):
        return self.assignments!=[]

    def results(self, method, asgn):
        del asgn["chooser"]
        del asgn["self"]

        class T3SubChart(T3Chart):
            @flow
            def subFlow(self, chooser):
                return method(chooser)
            subFlow.__name__ = method.__name__
            subFlow.__doc__  = method.__doc__

        assignments = []
        for subasgn in T3SubChart().assignments:
            newAsgn = asgn.copy()
            newAsgn.update(subasgn)
            assignments.append(newAsgn)
        return assignments


    def select(self, **kwd):
        solver = self.solver.solve(**kwd)
        chart  = self.__class__()
        # accept only dependent solutions as valid assignments
        # for a derived chart
        chart.assignments = solver.dependent
        chart.solver = solver
        return chart



if __name__ == '__main__':

    class ExampleT3Chart(T3Chart):

        @flow
        def r1(self, chooser):
            x = chooser.choose([0,1])
            y = chooser.choose([0,1])
            if x == 1:
                if y == 0:
                     z = 1
                else:
                     z = 0
            return vars()

        @flow
        def r2(self, chooser):
            z = chooser.choose([0,1])
            if z == 1:
                b = 1
            else:
                b = 0
            return vars()

        @flow
        def r3(self, chooser):
            p = chooser.choose([0,1])
            x = chooser.choose([0,1])
            if p == 1:
                if x == 0:
                     a = 1
                else:
                     a = 0
            return vars()

    chart = ExampleT3Chart()
    chart.create()
    print "Initial assignments"
    print "-"*20
    for asgn in chart.assignments:
        print asgn
    print "-"*20
    for asgn in chart.select(y=1).assignments:
        print asgn

    c = chart.select(x = 1)
    print c.assignments


    '''
    print "."*30
    print "Set b = 1"
    print "."*30
    solver = Solver(rbase.assignments)
    solver = solver.solve(b = 1)
    for asn in solver.assignments:
        print asn
    print "."*30
    print "Show only dependent assignments for which b = 1 has an impact"
    print "."*30
    for asn in solver.dependent:
        print asn
    print "."*30
    print "Set x = 1 for another solver"
    print "."*30
    solver = Solver(rbase.assignments)
    solver = solver.solve(x = 1)
    for asn in solver.assignments:
        print asn
    print "."*30
    print "Show only dependent assignments for which x = 1 has an impact"
    print "."*30
    for asn in solver.dependent:
        print asn
    print "."*30
    print "Set y = 0 on the same solver and show dependent results"
    print "."*30
    solver = solver.solve(y = 0)
    for asn in solver.dependent:
        print asn

    class ExampleT3Chart2(T3Chart):

        @flow
        def r1(self, chooser):
            S0 = chooser.choose(bool)
            S1 = chooser.choose([0,1])
            S2 = chooser.choose([0,1])
            S3 = chooser.choose([0,1])
            S4 = chooser.choose([0,1])
            A  = chooser.choose([0,1])
            if S0:
                A = 1
            elif (S1 and S2) or (S3 and S4):
                A = 1
            return vars()

    rbase = ExampleT3Chart2()
    solver = Solver(rbase.assignments)
    #solver = solver.solve(x = 1)
    print "."*30
    solver = solver.solve(S1 = 1)
    for asn in solver.dependent:
        print asn


    if rained:
        grass = wet
        sun_shining = false
    if sprinkler == on:
        grass = wet

    citizen_model = model {
        if BORN_IN_USA {
            US_CITIZEN = True;
        else if (US_RESIDENT and US_NATURALIZED) or \
            (MOTHER_US_CITITEN and US_REGISTERED) {
                US_CITIZEN = True;
        }
    }

    citizen_model.BORN_IN_USA        = {True, False};
    citizen_model.US_CITIZEN         = {True, False};
    citizen_model.MOTHER_US_CITIZEN  = {True, False};

    struct Person
    {
        citizen = new citizen_model()
        mother  = None
    }

    Person.citizen.MOTHER_US_CITIZEN <- Person.Mother.citizen.US_CITIZEN

    John = Person()
    Mary = Person()
    John.Mother = Mary
    Mary.citizen.US_CITIZEN = True
    '''


