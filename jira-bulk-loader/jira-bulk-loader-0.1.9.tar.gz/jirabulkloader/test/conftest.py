
import pytest


@pytest.fixture
def te():
    """TaskExtractor instance"""
    from jirabulkloader.task_extractor import TaskExtractor
    return TaskExtractor("http://jira.atlassian.com", "", "", dry_run = True)    


@pytest.fixture(scope='session')
def dry_run_key():
    """return the string 'DRY-RUN-XXXX'"""
    return 'DRY-RUN-XXXX'


@pytest.fixture(scope='session')
def std_te_input():
    """Standard input test for TaskExtractor.load testing"""
    import textwrap
    return textwrap.dedent( """
    h4. h4 task *assignee*
    =h4 task description
    # h4 sub-task *assignee*
    =h4 sub-task desc
    h5. h5.1 task *assignee*
    =h5.1 task desc
    # h5.1 sub-task *assignee*
    =h5.1 sub-task desc
    h5. h5.2 task *assignee*
    =h5.2 task desc
    # h5.2 sub-task *assignee*
    =h5.2 sub-task desc line1
    =h5.2 sub-task desc line2
    """ )


@pytest.fixture
def std_te_tasks():
    """Standard set of tasks for TaskExtractor.create_tasks testing"""
    return [
            {'assignee': 'assignee', 'markup': 'h4.', 'description': 'h4 task description', 'summary': 'h4 task', 'line_number': 2}, \
            {'assignee': 'assignee', 'markup': '#', 'summary': 'h4 sub-task', 'line_number': 4, 'description': 'h4 sub-task desc'}, \
            {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5.1 task', 'line_number': 6, 'description': 'h5.1 task desc'}, \
            {'assignee': 'assignee', 'markup': '#', 'description': 'h5.1 sub-task desc', 'summary': 'h5.1 sub-task', 'line_number': 8}, \
            {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5.2 task', 'line_number': 10, 'description': 'h5.2 task desc'}, \
            {'assignee': 'assignee', 'markup': '#', 'description': 'h5.2 sub-task desc line1\nh5.2 sub-task desc line2', \
            'summary': 'h5.2 sub-task', 'line_number': 12}, \
            ]

