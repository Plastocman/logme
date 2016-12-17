"""
DOC
"""
import sys
import imp
import ast
from ast_transformer import LogExceptions


class LoggerLoader(object):
    """
    helper class to load module. We do nothing on load_module call,
    the patch is done in the find_module method
    No need to expose it ?
    """

    def __init__(self, module):
        self.module = module

    def load_module(self, fullname):
        return self.module


class LoggerImporter(object):

    """
    This is the class which will hook on imports and apply the
    find_module method, to patch the AST before compiling it.
    """

    def __init__(self, log_file, include, exclude):
        """
        :param: include: the list of the includes you do want to patch
        :param: exclude: the list of files you don't want to patch, e.g.
                modules where catching errors is part of the program flow
                (common examples are StopIteration), or modules that catch
                too many exceptions that pollute your log file.

        Instances of this class will patch files iff their full names
        (i.e. full path) contains `include` and not any element of `exclude`

        Note : it is not recommended to patch big complex frameworks
        (e.g. Django, Twisted) as that usually just won't work for they
        already hacked import/parsing.

        If you want to  patch a django app
        you should add `django' in the exclude list.
        """

        self.log_file = log_file
        self.include = include
        self.exclude = exclude or []

    def find_module(self, fullname, path):
        """
        Check if the module pointed by `fullname` needs to be patched.
        If so, parse the module to get a parse tree, modify it,
        compile it and add the generated compiled code file to sys.modules.
        If not, just apply usual import/compilation/exectution.

        When this method returns None, Python will fallback to usual
        import, and no patch will be applied, hence the early returns.

        When it returns a Loader object (i.e. an object that provides
        a `load_module` method), it will apply the patch
        """

        for forbidden_name in self.exclude:
            if forbidden_name in fullname:
                return

        # this prevents patching outside your package
        # 'path' evaluates to `False` if not in a package
        if self.include not in fullname:
            return

        # note : `file` is just a  python fileobject
        # with the absolute path on your filesystem as name attribute
        # this is where we get the file reference

        file, pathname, description = imp.find_module(
            fullname.split(".")[-1], path)

        # file is `None` when you're importing a directory
        # you can't read, parse and patch a directory...
        if file is None:
            return

        src = file.read()
        tree = ast.parse(src)

        # this is where the magic happens
        tree = LogExceptions(self.include, self.log_file,
                             fullname, path).visit(tree)

        # some boilerplate
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__include__ = fullname.rpartition('.')[0]
        module.__file__ = file.name
        tree = ast.fix_missing_locations(tree)

        # AST compilation to bytecode
        code = compile(tree, file.name, "exec")

        # bytecode execution + module namespace filling, as usual
        try:
            exec code in module.__dict__
        # This happens when the execution of the module code itself crashes
        # I have no idea what to do with that, so I just fallback to normal
        # compilation/execution. Maybe add some logging ? You shouldn't
        # worry too much about that, as it's not related to the patching itself
        except Exception as e:
            with open(self.log_file, "a") as f:
                f.write("exec failed in {} : {}\n".format(fullname, e))
            return

        return LoggerLoader(module)


def do_hook(log_file='/dev/stdout', include='', exclude=None):
    """
    :param: string log_file: the name of the file you want to write the logs in
    :param: string include: the include you want to patch. It will apply
        the patch if and only if `include` is found as a substring of the
        module full path.
        Default to empty string, meaning you will patch everything.
        Not recommended though, you better filter it.
    :param: list exclude: the names of the modules you don't want to patch
    """
    sys.meta_path.append(LoggerImporter(log_file=log_file,
                                        include=include,
                                        exclude=exclude))
