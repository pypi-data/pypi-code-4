from ..tasks import Task
from ..util import SafeIterationSet

__all__ = ['TransformTask', 'TransformManager']
class TransformTask(object):
    def __init__(self, priority, rule_controller):
        """
        @param priority: The priority assigned to a TransformTask. TransformTasks run in serial.
        @param rule_controller: An instance of RuleManager that will be 
                             applied to every row in the dataset.
        """
        self.priority = priority
        self.validate(rule_controller)
        self.task = rule_controller.task_func
    
    def validate(self, rule_controller):
        if isinstance(rule_controller, RuleManager):
            if not rule_controller.filter.rc_map or rule_controller.rc_list:
                raise TransformError('Must have at least one rule controller in a rule manager.')
        
class TransformManager(object):
    def __init__(self, rule_tasks):
        """Manages the running of one or more TransformTasks.
        
        @param rule_tasks: A list of One or more TransformTasks
        """
        self._marks = SafeIterationSet()
        self.voided = False
        
        try:
            self.rule_tasks = sorted(rule_tasks, key=lambda task: task.priority)
        except (AttributeError, TypeError):
            raise(RuleError("RuleTasks must contain one or more RuleTasks")) 
    
    def run(self, data):
        """Run the RuleTasks based on priority. RuleTasks with the same priority
        will run in parallel otherwise they will run in serial.
        """ 
        for i, rule_task in enumerate(self.rule_tasks):
            data.add_task(Task(rule_task.task, 'RunRuleTask%i' % i))
        