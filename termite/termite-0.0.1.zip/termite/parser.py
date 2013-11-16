from termite.utils import create_task


def parse_yaml(elements, command_name):

    for root_element in elements:

        element_name, element_values = root_element.popitem()

        if element_name in ['cp', 'shell']:
            pass
            #parse_task(element_name, element_values)

        elif element_name == 'command':
            if element_values['name'] == command_name or command_name is None:
                command_name = element_values['name']
                parse_command(element_values)
        else:
            print('Unknow element: ', element_name)


def parse_command(command):
    for task in command['tasks']:
        name, args = task.popitem()
        create_task(name, args)
