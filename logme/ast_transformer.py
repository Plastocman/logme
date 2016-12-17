from ast import parse, NodeTransformer, Name, Store, fix_missing_locations


def tree_factory(template, **identifiers):
    """
    :param: string: template: the source code you want to inject
    :param: dict identifiers: the variables you want to inject in your template


    """
    source = template.format(**identifiers)
    return parse(source).body


# This is the code to inject to log every caught exception
# with its traceback
# don't mind the stupid file name, it's only here to avoid name conflicts
log_code = """import traceback
val = traceback.format_exc()
with open('{log_file}', 'a') as plz_be_a_free_name:
    plz_be_a_free_name.write('New caught error : \\n {{}} \\n'.format(val))"""


class LogExceptions(NodeTransformer):
    """
    This is the class that will visit and modify the syntax tree.
    It will call `visit_ExceptHandler` when it hits an ExceptHandler ast Node
    and add a logging instruction below it
    """

    def __init__(self, package, log_file, *args, **kw):
        """The `NodeTransformer` class has no __init__ method"""
        self.log_code = log_code
        self.log_file = log_file

    def visit_ExceptHandler(self, node):
        """adds logging after each caught exception in the program"""

        # does the node have a name for the caught exception ?
        try:
            exc_id = node.name.id
        # if not, give one
        except AttributeError:
            exc_id = 'ast_exc_id'
            node.name = Name(id=exc_id, ctx=Store())

        log_nodes = tree_factory(self.log_code, log_file=self.log_file)
        node.body = log_nodes + node.body
        fix_missing_locations(node)
        return node
