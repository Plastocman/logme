"""
This module defines a module finder, that will be called every time
you import a new module. It will parse the source code included in the file to
generate an ast that will be modified (in-place) by the ast_transformer module.

The modified ast will then be compiled into bytecode and put in cache as usual
and subsequent imports will refer to the modified bytecode. It allows you
to modify your code behavior without changing your sources.
"""

import sys
import imp
import ast
from ast_transformer import LogExceptions


class LoggerLoader(object):
    """
    Python expects the module finder to return a module loader that implements
    a load_module to call for later imports.
    Here we do nothing at load_module time, since all the work is done in the
    find_module method. SO this class simply returns the cached module.
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

    def __init__(self, log_file, required, exclude, packaged):
        """see the hook_imports docstring"""

        self.log_file = log_file
        self.required = required
        self.exclude = exclude or []
        self.packaged = packaged

    def find_module(self, fullname, path):
        """
        Check if the module pointed by `fullname` needs to be patched.
        If so, parse the module to get a parse tree, modifies it in-place,
        compile it and add the generated compiled code file to sys.modules.
        If not, just apply usual import/compilation/exectution.

        When this method returns None, Python will fallback to usual
        import, and no patch will be applied, hence the early returns.

        When it returns a Loader object (i.e. an object that provides
        a `load_module` method), it will apply the patch and push the
        patched module in the loader object (that will be used as a
        cache to later load the module)
        """

        for forbidden_name in self.exclude:
            if forbidden_name in fullname:
                return

        # this prevents patching outside your package
        if self.required not in fullname:
            return

        # 'path' evaluates to `False` if file is not in a package
        if self.packaged and not path:
            return

        # note : `file` is just a  python fileobject
        # with the absolute path on your filesystem as name attribute
        # this is where we get the file reference

        thefile, pathname, description = imp.find_module(
            fullname.split(".")[-1], path)

        # file is `None` when you're importing a directory
        # you can't read, parse and patch a directory...
        if thefile is None:
            return

        src = thefile.read()
        tree = ast.parse(src)

        # this is where the magic happens
        tree = LogExceptions(self.required, self.log_file,
                             fullname, path).visit(tree)

        # some boilerplate and metadatas handling for debug
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__include__ = fullname.rpartition('.')[0]
        module.__file__ = thefile.name
        tree = ast.fix_missing_locations(tree)

        # AST compilation to bytecode
        code = compile(tree, thefile.name, "exec")

        # bytecode execution + module namespace filling, as usual
        try:
            exec code in module.__dict__

        # This happens when the execution of the module code itself crashes
        # I have no idea what to do with that, so I just fallback to normal
        # compilation/execution. Maybe add some logging ? You shouldn't
        # worry too much about that, as it's not related to the patching itself
        # but it's actually an error in the source.
        except Exception as e:
            with open(self.log_file, "a") as f:
                f.write("exec failed in {} : {}\n".format(fullname, e))
            return

        return LoggerLoader(module)


def hook_imports(log_file='/dev/stdout', required='', exclude=None, packaged=False):
    """
    Hooks on import, and patches your code at import time to add a
    logging statement at the start of every exception handling block.
    This will not modify your sources, it only requires you to call this
    function once in your program entry point.

    This obviously won't work with C extensions.

    Examples:
        `from logme import hook_imports ; hook_imports()`
            will hook on imports
            will patch every module imported later on
            will write their caught exceptions with tracebacks to standard output

        `from logme import hook_imports
         hook_imports(log_file='/tmp/exc,
                      required='backend',
                      exclude=['module_1','module_2']
                      packaged=True)`

            will hook on imports
            will write caught exceptions into /tmp/exc
            will patch only modules whose file names match 'backend',
            will not patch modules whose file names match 'module_1' or 'module_2'
            will not patch modules that are not in a package

    :param: filename log_file: the file where you want to log your caught
        exceptions. Defaults to `/dev/stdout`, i.e. just printing them.

    :param: string required: the list of the package you do want to patch.
        It will check if the file full path includes the `required` string.
        Default to empty string, i.e. will match every imported file.

    :param: list exclude: a list of file names you don't want to patch,
        e.g. modules where catching errors is part of the program flow
        (common examples are StopIteration), or modules that catch
        too many exceptions that pollute your log file.

    :param: bool packaged: Defaults to False. If you set it to `True`,
        every module that is not in a package will not be patched.


    Note 1 : it is not recommended to patch big complex frameworks
    (e.g. Django, Twisted) as that usually just won't work for they
    already hacked imports/parsing. If you find a way to make it work
    let me know. For now, if you want to  patch a django app you should
    add `django' in the exclude list.

    Note 2 : if your application changes user during execution,
    it may raise an IOError when you try to write in the log file
    because of read/write permissions.
    You must be aware of that, the best solution is to add a
    context manager that temporarily drops/ acquires permissions
    and inject this context manager in the injected code (!)
    """
    sys.meta_path.append(LoggerImporter(log_file=log_file,
                                        required=required,
                                        exclude=exclude,
                                        packaged=packaged))
