import astroid

from collections import namedtuple, Counter

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class ChainedComparison(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'chained-comparison-checker'

    # here we define our messages
    msgs = {
        'R0294': ('simplify chained comparison',
                  'chained-comparison',
                  'check help',
                  ),
    }
    options = ()

    def _check_possible_chained_comparison(self, node):
        if node.op != 'and':
            return

        total_compares = len(node.values)
        if total_compares < 2:
            return

        # all node values must be compare
        for i in range(0, total_compares):
            if not isinstance(node.values[i], astroid.node_classes.Compare):
                return

        # collect all compares as tuple
        Comparison = namedtuple('Comparison', ['left_operand',
                                               'right_operand',
                                               'operator'])
        names = []
        comparisons = []
        for i in range(0, total_compares):
            if isinstance(node.values[i].left, astroid.node_classes.Name):
                names.append(node.values[i].left.name)
                left_operand = (node.values[i].left.name, 'name')
            else:
                left_operand = (node.values[i].left.name, 'const')

            if isinstance(node.values[i].ops[0][1], astroid.node_classes.Name):
                names.append(node.values[i].ops[0][1].name)
                right_operand = (node.values[i].ops[0][1].name, 'name')
            else:
                right_operand = (node.values[i].ops[0][1], 'const')

            operator = node.values[i].ops[0][0]
            comparisons.append(Comparison(left_operand, right_operand, operator))

        counter = Counter(names)
        for item in counter.items():
            if item[1] > 1:
                lower_bound = False
                upper_bound = False
                # search this name in comparisons
                for i in range(0, total_compares):
                    if comparisons[i].left_operand[1] == 'name' and comparisons[i].left_operand[0] == item[0]:
                        if comparisons[i].operator == '<':
                            upper_bound = True
                        elif comparisons[i].operator == '>':
                            lower_bound = True
                    elif comparisons[i].right_operand[1] == 'name' and comparisons[i].right_operand[0] == item[0]:
                        if comparisons[i].operator == '<':
                            lower_bound = True
                        elif comparisons[i].operator == '>':
                            upper_bound = True

                # suggestion = "variable '%s' can be chained in comparison" % (item[0],)

                if lower_bound and upper_bound:
                    self.add_message('chained-comparison',
                                     node=node)

    def visit_boolop(self, node):
        self._check_possible_chained_comparison(node)


def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(ChainedComparison(linter))
