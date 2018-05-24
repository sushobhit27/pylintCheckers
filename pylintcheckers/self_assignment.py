import astroid

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class SelfAssignmentChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'self-assignment-checker'

    # here we define our messages
    msgs = {
        'W0634': ('Assigning %s to itself',
                  'assignment-to-itself',
                  'This message occurs when a variable is assigned to itself.',
                  ),
    }
    options = ()

    def _check_self_assignment(self, node):
        values = node.targets
        values.append(node.value)
        if all(not isinstance(value, (astroid.Name, astroid.AssignName)) for value in values):
            return

        names = set()
        for value in values:
            if value.name in names:
                self.add_message('assignment-to-itself', node=node, args=value.name)
            else:
                names.add(value.name)

    def visit_assign(self, node):
        self._check_self_assignment(node)


def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(SelfAssignmentChecker(linter))
