#!/usr/bin/python

#-*- coding: UTF-8 -*-

from jirabulkloader.task_extractor import TaskExtractor
from jirabulkloader.task_extractor_exceptions import TaskExtractorTemplateErrorProject, TaskExtractorJiraValidationError, TaskExtractorTemplateErrorJson, TaskExtractorJiraCreationError

import unittest
from mock import MagicMock, call
import simplejson as json

class TestTaskExtractor(unittest.TestCase):
  
  def setUp(self):
    self.jira_url = "http://jira.atlassian.com" # MUST BE CHANGED
    options = {}
    self.te = TaskExtractor(self.jira_url, "", "", options, dry_run = True)

  def tearDown(self):
    self.te = None

##########################################################
### validate_load

  def test_validate_load_call_validate_user_with_correct_parameters(self):
    input_task_list = [{'assignee': 'user1', 'markup': 'h5.', 'summary': 'h5 task', 'tmpl_ext':{"project": {"key": "project1"}}}, \
        {'text':'sample text'}, \
        {'assignee': 'user2', 'markup': 'h5.', 'summary': 'h5 task', 'tmpl_ext':{"project": {"key": "project2"}}}]
    self.te._validate_user = MagicMock()
    expected_result = [call('user1', 'project1'), call('user2', 'project2')]
    self.te.validate_load(input_task_list)
    self.assertEquals(self.te._validate_user.call_args_list, expected_result)

  def test_validate_load_raise_error_if_no_project(self):
    input_task_list = [{'assignee': 'user1', 'markup': 'h5.', 'summary': 'h5 task'}]
    self.te._validate_user = MagicMock()
    self.assertRaises(TaskExtractorTemplateErrorProject, self.te.validate_load, input_task_list)

##########################################################
### load

  def test_load_Text_h4_and_h5_with_empty_line(self):
    input_text = "\n\nh4. h4 task *assignee*\n\nh5. h5 task *assignee*"
    excpected_result = [{'assignee': 'assignee', 'markup': 'h4.', 'summary': 'h4 task', 'line_number': 3}, \
            {'text':''}, {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'line_number': 5}]
    self.assertEquals(excpected_result, self.te.load(input_text))

  def test_load_Text_h5_and_sub_task_with_empty_line(self):
    input_text = "h5. h5 task *assignee*\n\n#* Sub-task 1 *assignee*\n\n#* Sub-task 2 *assignee*"
    excpected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'line_number': 1}, \
            {'text':''}, \
            {'assignee': 'assignee', 'markup': '#*', 'summary': 'Sub-task 1', 'line_number': 3}, {'text':''}, \
            {'assignee': 'assignee', 'markup': '#*', 'summary': 'Sub-task 2', 'line_number': 5}]
    self.assertEquals(excpected_result, self.te.load(input_text))

  def test_load_Check_dueDate(self):
    input_text = "h5. h5 task *assignee* %2012-04-01%\n=line1 description"
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 1, 'description':'line1 description', 'duedate':'2012-04-01'}]
    self.assertEquals(expected_result, self.te.load(input_text))

  def test_load_Recognize_template_variables(self):
    input_text = "[VAR1=1]\n[VAR2=2]\nh5. h5 task *assignee* %2012-04-01%\n=line1 description"
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 3, 'description':'line1 description', 'duedate':'2012-04-01'}]
    self.assertEquals(expected_result, self.te.load(input_text))
    self.assertEquals({'VAR1':'1', 'VAR2':'2'}, self.te.tmpl_vars)

  def test_load_Text_replacement(self):
    input_text = "[VAR1=h5.]\n[VAR2= h5 task]\n$VAR1$VAR2 *assignee*"
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'line_number': 3}]
    self.assertEquals(expected_result, self.te.load(input_text))

  def test_load_Variable_with_similar_name(self):
    input_text1 = "[VAR=h5.]\n[VAR_VAR= task]\nh5. $VAR_VAR$VAR_VAR *assignee*"
    input_text2 = "[VAR_VAR= task]\n[VAR=h5.]\n$VAR $VAR_VAR$VAR_VAR *assignee*"
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'line_number': 3, 'summary': 'task task'}]
    self.assertEquals(expected_result, self.te.load(input_text1))
    self.assertEquals(expected_result, self.te.load(input_text2))

  def test_load_Recognize_template_json(self):
    input_text = '{"item1":{"name":"test"}}'
    self.te.load(input_text)
    self.assertEquals({'item1':{'name':'test'}}, self.te.tmpl_json)

  def test_load_JSON_variable_must_be_replaced_by_new_value(self):
    input_text = '{"item1":{"name":"test"}}\n{"item1":{"name":"newtest"}}'
    self.te.load(input_text)
    self.assertEquals({'item1':{'name':'newtest'}}, self.te.tmpl_json)

  def test_load_json(self):
    input_text = '{"item1":{"name":"test"}}\nh5. h5 task *assignee*'
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 2, 'tmpl_ext':{'item1':{'name':'test'}}}]
    self.assertEquals(expected_result, self.te.load(input_text))

  def test_load_json_if_it_is_not_valid(self):
    input_text = '{fail test}'
    self.assertRaises(TaskExtractorTemplateErrorJson, self.te.load, input_text)

  def test_load_Check_dueDate_and_JSON_in_one_line(self):
    input_text = 'h5. h5 task1 *assignee* %2012-04-01% {"item2":"test2"}\nh5. h5 task2 *assignee*'
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task1', \
            'duedate':'2012-04-01', 'tmpl_ext':{"item2":"test2"}, 'line_number': 1}, \
            {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task2', 'line_number': 2}]
    self.assertEquals(expected_result, self.te.load(input_text))

  def test_load_Check_JSON_inline(self):
    input_text = '{"item1":{"name":"test"}}\nh5. h5 task *assignee* {"item2":"test2"}'
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 2, 'tmpl_ext':{"item1":{"name":"test"}, "item2":"test2"}}]
    self.assertEquals(expected_result, self.te.load(input_text))

  def test_load_Check_JSON_inline_replacement(self):
    input_text = '{"item1":{"name":"test"}}\n{"item2":"test2"}\nh5. h5 task *assignee* {"item1":"test1"}\n#* Sub-task 1 *assignee*'
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 3, 'tmpl_ext':{"item1":"test1", "item2":"test2"}}, \
            {'assignee': 'assignee', 'markup': '#*', 'summary': 'Sub-task 1', \
            'line_number': 4, 'tmpl_ext':{"item1":{"name":"test"}, "item2":"test2"}}]
    self.assertEquals(expected_result, self.te.load(input_text))


##########################################################
### create_tasks

  def test_create_tasks_Single_h4_task_with_sub_task(self):
    self.te.create_issue = MagicMock()
    self.te.create_issue.return_value = 'DRY-RUN-XXXX'
    input_list = [{'assignee': 'assignee', 'markup': 'h4.', 'description': 'h4 task description', 'summary': 'h4 task'}, \
            {'assignee': 'assignee', 'markup': '#', 'summary': 'sub-task'}]
    expected_result = [call({'issuetype': 'User Story', 'assignee': 'assignee', 'markup': 'h4.', \
            'description': 'h4 task description', 'summary': 'h4 task'}), \
            call({'issuetype': 'Sub-task', 'assignee': 'assignee', 'markup': '#', \
            'parent' : 'DRY-RUN-XXXX', 'summary': 'sub-task'})]
    expected_output = 'h4. h4 task (DRY-RUN-XXXX)\n# sub-task (DRY-RUN-XXXX)'
    self.assertEquals(self.te.create_tasks(input_list), expected_output)
    self.assertEquals(self.te.create_issue.call_args_list, expected_result)

  def test_create_tasks_Single_h5_task(self):
    self.te.create_issue = MagicMock()
    self.te.create_issue.return_value = 'DRY-RUN-XXXX'
    self.te.update_issue_desc = MagicMock()
    input_list = [{'assignee': 'assignee', 'markup': 'h5.', 'description': 'h5 task description', 'summary': 'h5 task'}]
    expected_result = {'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'description': 'h5 task description', 'summary': 'h5 task'}
    expected_output = 'h5. h5 task (DRY-RUN-XXXX)\nh5 task description'
    self.assertEquals(self.te.create_tasks(input_list), expected_output)
    self.te.create_issue.assert_called_once_with(expected_result)
    self.assertEquals(self.te.update_issue_desc.call_count, 0)

  def test_create_tasks_Several_tasks(self):
    self.te.create_issue = MagicMock()
    self.te.create_issue.return_value = 'DRY-RUN-XXXX'
    self.te.update_issue_desc = MagicMock()
    input_list = [{'assignee': 'assignee', 'markup': 'h4.', 'description': 'h4 task description', 'summary': 'h4 task'}, \
      {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'description': 'h5 task description'}, \
      {'assignee': 'assignee', 'markup': '#', 'description': 'line1 description\nline2 description', 'summary': 'sub-task'}]
    expected_result = [call({'issuetype': 'User Story', 'assignee': 'assignee', 'markup': 'h4.', \
        'description': 'h4 task description', 'summary': 'h4 task'}), \
        call({'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'description': \
        'h5 task description', 'summary': 'h5 task'}), \
        call({'description': 'line1 description\nline2 description', 'parent': 'DRY-RUN-XXXX', \
        'markup': '#', 'summary': 'sub-task', 'assignee': 'assignee', 'issuetype': 'Sub-task'})]
    self.te.create_tasks(input_list)
    self.assertEquals(self.te.create_issue.call_args_list, expected_result)
    MagicMock.assert_called_once_with(self.te.update_issue_desc, 'DRY-RUN-XXXX', 'h5 task description\n# sub-task (DRY-RUN-XXXX)')

  def test_create_tasks_Several_tasks_without_description(self):
    self.te.create_issue = MagicMock()
    self.te.create_issue.return_value = 'DRY-RUN-XXXX'
    self.te.update_issue_desc = MagicMock()
    input_list = [{'assignee': 'assignee', 'markup': 'h4.', 'summary': 'h4 task'}, \
      {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task'}, \
      {'assignee': 'assignee', 'markup': '#', 'summary': 'sub-task'}]
    expected_result = [call({'issuetype': 'User Story', 'assignee': 'assignee', 'markup': 'h4.', 'summary': 'h4 task'}),
        call({'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task'}),
        call({'parent': 'DRY-RUN-XXXX', 'markup': '#', 'summary': 'sub-task', 'assignee': 'assignee', 'issuetype': 'Sub-task'})]
    expected_output = 'h4. h4 task (DRY-RUN-XXXX)\nh5. h5 task (DRY-RUN-XXXX)\n# sub-task (DRY-RUN-XXXX)'
    self.assertEquals(self.te.create_tasks(input_list), expected_output)
    self.assertEquals(self.te.create_issue.call_args_list, expected_result)
    MagicMock.assert_called_once_with(self.te.update_issue_desc, 'DRY-RUN-XXXX', '# sub-task (DRY-RUN-XXXX)')

  def test_create_tasks_Tasks_with_text(self):
    self.te.create_issue_http = MagicMock()
    self.te.create_issue_http.return_value = 'DRY-RUN-XXXX'
    input_list = [{'assignee': 'assignee', 'markup': 'h4.', 'summary': 'h4 task'}, \
        {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'description':'h5 desc'}, {'text':'text line'}, \
        {'assignee': 'assignee', 'markup': '#', 'summary': 'sub-task'}]
    expected_result = 'h4. h4 task (DRY-RUN-XXXX)\nh5. h5 task (DRY-RUN-XXXX)\nh5 desc\ntext line\n# sub-task (DRY-RUN-XXXX)'
    self.assertEquals(self.te.create_tasks(input_list), expected_result)

  def test_create_tasks_Tasks_with_no_h4_task(self):
    self.te.create_issue = MagicMock()
    self.te.create_issue.return_value = 'DRY-RUN-XXXX'
    input_list = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task 1'}, \
        {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task 2'}, \
        {'assignee': 'assignee', 'markup': '#', 'summary': 'sub-task of h5 task 2'}]
    expected_result = [call({'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task 1'}), \
        call({'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task 2'}), \
        call({'parent': 'DRY-RUN-XXXX', 'markup': '#', 'summary': 'sub-task of h5 task 2', 'assignee': 'assignee', 'issuetype': 'Sub-task'})]
    expected_output = 'h5. h5 task 1 (DRY-RUN-XXXX)\nh5. h5 task 2 (DRY-RUN-XXXX)\n# sub-task of h5 task 2 (DRY-RUN-XXXX)'
    self.assertEquals(self.te.create_tasks(input_list), expected_output)
    self.assertEquals(self.te.create_issue.call_args_list, expected_result)

##########################################################
### jira_format

  def test_jira_format_Simple_case(self):
    input_dict = {'parent': 'DRY-RUN-XXXX', 'markup': '#', 'summary': 'sub-task', 'assignee': 'assignee', 'issuetype': 'Sub-task'}
    expected_result = {'fields': { 'parent': {'key': 'DRY-RUN-XXXX'}, \
        'summary': 'sub-task', 'assignee': {'name': 'assignee'}, 'issuetype': {'name': 'Sub-task'}}}
    self.assertEquals(self.te.jira_format(input_dict), expected_result)

  def test_jira_format_If_additional_fields_provided(self): 
    options = {'project': {'key':'TestProject'}, 'item1':['subitem1', 'subitem2']}
    self.te = TaskExtractor(self.jira_url, "", "", options, dry_run = True)
    input_dict = {'parent': 'DRY-RUN-XXXX', 'markup': '#', 'summary': 'sub-task', 'assignee': 'assignee', 'issuetype': 'Sub-task'}
    expected_result = {'fields': {'parent': {'key': 'DRY-RUN-XXXX'}, 'summary': 'sub-task', 'project': {'key': 'TestProject'}, \
         'assignee': {'name': 'assignee'}, 'issuetype': {'name': 'Sub-task'}, 'item1':['subitem1', 'subitem2']}}
    self.assertEquals(self.te.jira_format(input_dict), expected_result)

  def test_jira_format_Replaces_default_params_by_tmpl_json(self):
    options = {'project': {'key':'TestProject'}, 'duedate':'2012-03-01', 'item1':'default_value'}
    self.te = TaskExtractor(self.jira_url, "", "", options, dry_run = True)
    input_json = {'duedate':'2012-04-01', 'issuetype': 'Task', 'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'tmpl_ext':{'item1':'template_value'}}
    expected_result = {'fields': {'summary': 'h5 task', 'project': {'key': 'TestProject'}, 'duedate':'2012-04-01', \
          'assignee': {'name': 'assignee'}, 'issuetype': {'name': 'Task'}, 'item1':'template_value'}}
    self.assertEquals(self.te.jira_format(input_json), expected_result)


##########################################################
### run-time variables

  def test_load_recognize_run_time_variables(self):
    input_text = "[VAR1=1]\nh5. h5 task *assignee* [TASK_KEY]\n=line1 description"
    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', \
            'line_number': 2, 'description':'line1 description', 'rt_ext':'TASK_KEY'}]
    self.assertEquals(expected_result, self.te.load(input_text))
    self.assertEquals({'VAR1':'1'}, self.te.tmpl_vars)

  def test_create_issue_add_rt_var(self):
    test_issue_id = 'TEST-RUN-XXXX'
    self.te._create_issue_http = MagicMock()
    self.te._create_issue_http.return_value = test_issue_id
    input_dict = {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task', 'rt_ext':'TASK_KEY'}
    self.assertEquals(test_issue_id, self.te.create_issue(input_dict))
    self.assertEquals({'TASK_KEY':test_issue_id}, self.te.rt_vars)

  def test_create_issue_replace_rt_variable(self):
    input_text = """
h5. h5 task1 *assignee* [TASK_KEY1]
h5. h5 task2 *assignee* [TASK_KEY2]
h5. h5 task3 *assignee*
=description $TASK_KEY1
# Sub-task *assignee*
=description $TASK_KEY2
"""
    test_issue_id = 'TEST-RUN-XXXX'
    self.te._create_issue_http = MagicMock()
    self.te._create_issue_http.return_value = test_issue_id
    self.te.update_issue_desc = MagicMock()

    expected_result = [{'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task1', 'rt_ext':'TASK_KEY1', 'line_number': 2},
            {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task2', 'rt_ext':'TASK_KEY2', 'line_number': 3},
            {'assignee': 'assignee', 'markup': 'h5.', 'summary': 'h5 task3', 'description':'description $TASK_KEY1', 'line_number': 4},
            {'assignee': 'assignee', 'markup': '#', 'summary': 'Sub-task', 'description':'description $TASK_KEY2', 'line_number': 6}]
    load_result = self.te.load(input_text)
    self.assertEquals(expected_result, load_result)

    expected_result_load = 'h5. h5 task1 (TEST-RUN-XXXX)\nh5. h5 task2 (TEST-RUN-XXXX)\nh5. h5 task3 (TEST-RUN-XXXX)\ndescription TEST-RUN-XXXX\n# Sub-task (TEST-RUN-XXXX)'
    self.assertEquals(self.te.create_tasks(load_result), expected_result_load)
    self.te.update_issue_desc.assert_called_once_with(test_issue_id, 'description TEST-RUN-XXXX\n# Sub-task (TEST-RUN-XXXX)')


#if __name__ == "__main__":
#      unittest.main()

import nose
nose.run(argv=["", "test_task_extractor", "--verbosity=2"])

