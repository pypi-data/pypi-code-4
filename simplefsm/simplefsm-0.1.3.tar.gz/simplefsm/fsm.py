''' The main class for simplefsm'''
from .exceptions import (
    InvalidStateError,
    MethodNotAllowedError,
    InconsistentModelError,
)


def validate_model(initial_state, model):
    '''Ensure the model is self-consistent'''
    # Is initial_state one of the states in the model?
    if initial_state and initial_state not in model:
        raise InconsistentModelError(
            "Initial state '%s' does not match "
            "any valid state." % initial_state
        )
    invalid_states = []
    for _, transitions in model.iteritems():
        for state in transitions:
            if state not in model:
                invalid_states.append(state)
    if invalid_states:
        raise InconsistentModelError(
            "Transition definition references non-existent state%s: '%s'." %
            ('s'[len(invalid_states) == 1:], "', '".join(invalid_states))
        )


class SimpleFSM(object):
    '''A Simple State Machine, with the following goals:

        - Minimalistic/Concise: defining the model should be concise and
          readable
        - Simple API: public methods should be few
        - Fast: the performance of lookups and validations should be as close
          as possible to the speed of Python's built-in types
    '''
    def __init__(self, state_model):
        '''Capture transitions and (optionally) initial state

        - No initial state means any state can be the first state
        - Setting initial state restricts first change to a valid transition
        '''
        if not state_model:
            raise ValueError(
                'The passed-in state model cannot by empty or None.'
            )
        self.current = state_model.get('initial', None)
        self._model = state_model.get('transitions', {})
        validate_model(self.current, self._model)
        self._last_change_to = None
        self._reached = False

    def change_to(self, new_state):
        '''Attempts to progress to the state indicated by new_state'''
        self._last_change_to = new_state  # For force_change_to logic
        if self.current is None and new_state not in self._model:
                raise InvalidStateError(
                    "Cannot change state. '%s' is not a valid state." %
                    new_state
                )
        elif self.current is not None and self.restricted(new_state):
            raise InvalidStateError(
                "Attempted change to state '%s' is not permitted." %
                new_state
            )
        self.current = new_state

    def force_change_to(self, new_state):
        '''If an attempted change_to for new_state failed,
        force the change anyway
        '''
        if new_state is self._last_change_to:
            self.current = new_state
        else:
            raise MethodNotAllowedError(
                "'force_change_to' can only be called after a "
                "failed call to 'change_to' for the same state."
            )

    def permitted(self, next_state):
        '''returns True if a state change is permitted'''
        return next_state in self._model[self.current]

    def restricted(self, next_state):
        '''returns True if a state change is not permitted'''
        return not self.permitted(next_state)

    def reachable(self, desired_state):
        '''Convenience method wrapping the recursive _reachable'''
        self._reached = False
        return self._reachable(desired_state, self.current, set())

    def _reachable(self, desired_state, current_state, visited):
        '''Recursive Breadth First Search'''
        visited.add(current_state)
        if not self._reached:
            self._reached = current_state == desired_state
            if not self._reached and self._model.get(current_state):
                for next_state in self._model[current_state]:
                    if next_state not in visited:
                        self._reachable(desired_state, next_state, visited)
        return self._reached
