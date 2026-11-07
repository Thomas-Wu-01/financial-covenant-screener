from contract import Task, Tool

from . import screen, tools


def verify_input(tool, value):
    return tools.verify_list_input(value) if Tool(tool) == Tool.LIST_COVENANT_FACTS else tools.verify_read_input(value)


def verify_output(tool, input_value, output_value, workspace):
    return (
        tools.verify_list_output(input_value, output_value, workspace)
        if Tool(tool) == Tool.LIST_COVENANT_FACTS
        else tools.verify_read_output(input_value, output_value, workspace)
    )


def verify_task(task, arguments, output, reference, workspace):
    if Task(task) == Task.SCREEN_COVENANTS:
        return screen.verify_task(arguments, output, reference, workspace)
