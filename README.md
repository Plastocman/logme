# Python code injection

## What does it do ?


For those who know, this is pretty much the opposite of [fuckit](https://github.com/ajalt/fuckitpy)


This module will add logging after every single exception handler. That means that **every** exception that is caught in your code will now be logged.

Whether it's useful or not depends mainly on your program flow and the quality of your exception handling, but it can come in handy.

## How does it work ?

This module will hook on imports, catch the syntax trees generated by the parser and rewrite them before yielding them to the compiler, therefore modifying your code behavior without changing the sources. 

### import hooks

See [PEP 302](https://www.python.org/dev/peps/pep-0302/) and stdlib doc for import hooks. 

Basically you're patching the `import` statement, giving new methods for finding/loading modules in your program, which allows you to do pretty much anything you want to your sources before compiling them, like adding/removing lines of code or rewriting some statements for example.

### AST 

The ast module helps you modify your code at runtime. AST are an intermediate representation of code, which are much easier to modify/analyse programmatically than source code.

The classes inheriting from ast.NodeTransformer take a parse tree as input and modify it berore returning it. The modified syntax tree will then be compiled into CPython bytecode.

See [greentreesnakes](https://greentreesnakes.readthedocs.io/en/latest/) and the stdlibdoc for the AST.


## Usage

git clone this repo and

    python setup.py install

then all you have to do is add this line :

    from logme import do_hook ; do_hook()

After this statement, every module imported will have its ast patched to log every caught exception.

You can add optional parameters to the `do_hook` function :
- change the logfile (default is `/dev/stdout`)
- choose to ban some files from patching (default to `None`)
- chose to ban only some files 

Coming soon : console script + pypi

## Caveats

Can take a little extra time to start your program.

Log files may be polluted by exceptions that are part of your program flow, like StopIteration and AttributeError used as state checking and whatnot. 


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

You should be able to play with the source since the code is very compact (under 100 LOC !) and rather simple. The possibilities with ast + import hooks are endless, and it's actually really fun. Feel free to contact me if you have any idea/pull request to improve it !
