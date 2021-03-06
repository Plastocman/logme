# Python error logger

Stuck with legacy code ? Python can help.

Logme uses a combination of import hooks and abstract syntax trees rewriting to log every exception (with their tracebacks) that is caught by your code, even those who have been silenced out by distracted programmers.

For those who know, this is pretty much the opposite of [fuckit](https://github.com/ajalt/fuckitpy)

## How does it work ?

This module will hook on imports, and then for every imported module catch the syntax trees generated by the parser and modify them before yielding them to the compiler, therefore modifying your code behavior without changing your sources. Basically it will replace every 
```
except SomeException:
    somecodeblock	
``` 

and 

```
except SomeException as e:
    somecodeblock
```

by a new code :

```
except SomeException as e:
    log(e, traceback)
    somecodeblock
```



### import hooks

See [PEP 302](https://www.python.org/dev/peps/pep-0302/) and standard lib doc for import hooks. 

Basically you're patching the `import` statement, giving new methods for finding/loading modules in your program, which allows you to do pretty much anything you want to your sources before compiling them, like adding/removing lines of code or rewriting some statements for example.

### AST 

The ast module helps you modify your code at runtime. AST are an intermediate representation of code, which are much easier to modify/analyse programmatically than source code.

The classes inheriting from ast.NodeTransformer take a parse tree as input and modify it berore returning it. The modified syntax tree will then be compiled into CPython bytecode.

See [greentreesnakes](https://greentreesnakes.readthedocs.io/en/latest/) and the standard lib doc for the AST.


## Usage

git clone this repo and

    python setup.py install

then all you have to do is go to your program entry point and add this statement :

    from logme import hook_imports ; hook_imports()

After this statement, every module imported will have its ast patched to log every caught exception.

The `hook_imports` function also has optionnal parameters :
- change the logfile (default is `/dev/stdout`), i.e. where to write the caught exceptions.
- choose to ban some files from patching (default to `None`)
- chose to patch only some specific files, i.e. sometimes you will patch only your package.

Coming soon : console launcher + release on pypi.

## Caveats

Can take a little extra time to start your program.

Log files may be polluted by exceptions that are part of your program flow, like StopIteration and AttributeError used as state checking and whatnot. Use the `exclude` argument to `hook_impports` to prevent that.


## Is it useful ? 

It's mainly intended for debugging/testing big code bases, and not meant to be used in production. 

I'm sure you will love it if some of your co-workers are found of the infamous
```
try:
    |
    |
    |
    1300 lines of branches
    |
    |
    |
except:
    pass
```

 design pattern.

## What's next ?

AST and import hooks make it really easy to create a code injection/modification lib/framework, without changing your sources.

You should be able to play with the source since the code is very compact (under 100 LOC) and rather simple. The possibilities with ast + import hooks are endless, and it's actually really fun. Feel free to contact me if you have any idea/pull request to improve it !

Python 3 shall not be a priority since our goal is mostly to deal with legacy code...