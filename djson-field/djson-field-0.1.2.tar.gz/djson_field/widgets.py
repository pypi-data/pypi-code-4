# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.forms.widgets import Textarea
from django.template.loader import render_to_string

import json
import string
import re


def update_tree(tree, path, value):
    if len(path) > 0:
        is_add = value not in ["__KEEP_LIST__", "__KEEP_DICT__"]
        if path[0].startswith("_"):
            if not tree:
                tree = {}
            if is_add or len(path) > 1:
                index = path[0][1:]
                tree[index] = tree.get(index)
        else:
            if not tree:
                tree = []
            if is_add or len(path) > 1:
                index = int(path[0])
                while len(tree) <= index:
                    tree.append(None)
        if len(path) == 1:
            if is_add:
                tree[index] = value
        else:
            tree[index] = update_tree(tree[index], path[1:], value)
    return tree


def parse_name(name):
    nodes = []
    node = u""
    is_start = False
    for char in name:
        if char == "[":
            is_start = True
        elif char == "]":
            nodes.append(node)
            node = u""
            is_start = False
        elif is_start:
            node += char
    return nodes


def get_name_by_path(base, path):
    return base + string.join(["[%s]" % (ob if isinstance(ob, int) else "_" + ob) for ob in path], '')


def remove_empty_items(tree):
    if type(tree) == list:
        return [remove_empty_items(ob) for ob in tree if ob is not None]
    elif type(tree) == dict:
        for key, value in tree.iteritems():
            tree[key] = remove_empty_items(value)
    return tree


def is_satisfy_selectors(selectors, path):
    if len(selectors) == 0:
        return True
    if len(path) == 0:
        return False
    for i in xrange(1, len(path) + 1):
        if type(selectors[-1]) in [unicode, str, int, long]:
            condition = selectors[-1] == path[-i]
        else:
            node = path[-i]
            if type(node) in [int, long]:
                node = str(node)
            match = re.match(selectors[-1], node)
            condition = match and match.end() == len(node)
        if condition:
            return is_satisfy_selectors(selectors[:-1], path[:-i])
    return False


class JSONWidget(Textarea):

    ADD_ACTIONS = {
        "add_plain": u"простое значение",
        "add_list": u"список",
        "add_dict": u"словарь",
    }

    NAME_PATTERN = "%%NAME%%"

    def __init__(self, rules=[], *args, **kwargs):
        self.rules = rules
        super(JSONWidget, self).__init__(*args, **kwargs)

    def add_links_template(self, rules):
        actions = rules.get('actions', [])
        link_actions = [ob for ob in actions if ob in self.ADD_ACTIONS]
        links = {key: value for key, value in self.ADD_ACTIONS.iteritems()
                 if key in link_actions}
        if len(link_actions) > 0:
            return render_to_string("djson_field/add_links.html", {
                'links': links,
            })
        return ""

    def get_rules(self, path):
        rules = {}
        for selectors, _rules in self.rules[::-1]:
            if is_satisfy_selectors(selectors, path):
                for key, rule in _rules.iteritems():
                    if key not in rules:
                        rules[key] = rule
        return rules

    def get_templates(self, path):
        rules = self.get_rules(path)
        return {
            'dict': self.render_data(self.NAME_PATTERN, {}, path=[],
                                     with_templates=False, rules=rules),
            'list': self.render_data(self.NAME_PATTERN, [], path=[],
                                     with_templates=False, rules=rules),
            'plain': self.render_data(self.NAME_PATTERN, u"", path=[],
                                      with_templates=False, rules=rules)
        }

    def render_field(self, name, data, path, field=None, rules=None):
        rules = rules if rules else self.get_rules(path)
        field = field if field else rules['type']
        field_name = get_name_by_path(name, path)
        if isinstance(field, dict):
            key = path[-1] if len(path) > 0 else None
            items = OrderedDict([(key, self.render_field(name, None, path + [key], ob)) for key, ob in field.iteritems()])
            return render_to_string("djson_field/complex_field.html", {
                'name': field_name,
                'key': key if not isinstance(key, int) else None,
                'rules': rules,
                'items': items
            })
        field = field.formfield().widget.render(field_name, data)
        match = re.match(r'<[a-zA-Z0-9._]+\s+', field)
        if match:
            field = field[:match.end()] + ' class="jsonFieldItemValue" ' + field[match.end():]
        return field

    def render_data(self, name, data, path=[], rules=None, with_templates=True):
        rules = rules or self.get_rules(path)
        key = path[-1] if len(path) > 0 else None
        field_name = get_name_by_path(name, path)
        field = self.render_field(name, data, path, rules=rules)
        field_key = rules['type_key'] and rules['type_key'].formfield().widget.render("__%s" % field_name, key)
        if field_key:
            match = re.match(r'<[a-zA-Z0-9._]+\s+', field_key)
            if match:
                field_key = field_key[:match.end()] + ' class="jsonFieldItemKey" ' + field_key[match.end():]
        params = {
            'field': field,
            'field_key': field_key,
            'name': field_name,
            'key': key if not isinstance(key, int) else None,
            'controls': self.add_links_template(rules),
            'rules': rules,
            'templates': with_templates and self.get_templates(path + (isinstance(key, int) and [0] or ['']))
        }
        if isinstance(data, dict):
            params['items'] = OrderedDict(
                [(key, self.render_data(name, ob, path + [key])) for key, ob in data.iteritems()])
            template = "djson_field/dictionary_item.html"
        elif isinstance(data, list):
            params['items'] = ((None, self.render_data(name, ob, path + [i])) for i, ob in enumerate(data))
            template = "djson_field/list_item.html"
        else:
            params['value'] = data
            template = "djson_field/plain_item.html"
        return render_to_string(template, params)

    def render(self, name, value, attrs=None):
        json_dict = {}
        if value and len(value) > 0:
            json_dict = json.loads(value)
        html = self.render_data(name, json_dict)
        return render_to_string("djson_field/base.html", {
            'content': html
        })

    def value_from_datadict(self, data, files, name):
        value = None
        for key, val in data.iteritems():
            if key.startswith(name):
                if key.startswith(name + '['):
                    branch_keys = parse_name(key)
                    value = update_tree(value, branch_keys, val)
                else:
                    value = val
                    break
        if isinstance(value, list) or isinstance(value, dict):
            value = remove_empty_items(value)
        if value:
            value = json.dumps(value)
        return value

    class Media:
        css = {
            'all': ('css/djson_field.css',)
        }
        js = ('js/djson_field.js',)
