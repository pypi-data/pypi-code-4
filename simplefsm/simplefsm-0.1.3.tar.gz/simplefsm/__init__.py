'''SimpleFSM: a simple finite state machine'''

# Set modules up directly under the simplefsm package
__all__ = ['SimpleFSM', 'validate_model']

from .fsm import SimpleFSM, validate_model
