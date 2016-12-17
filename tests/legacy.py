"""
You can use it as a minimal test : if this module execution (e.g. on import)
outputs any Exception/traceback that means your code most likely works
"""

print """
I am some great unmaintained code straight from 2008.
I was written in 2 days by someone trying to teach herself Python, 
and you're gonna love me.
"""



def some_stupid_function(mutable_shared_state, *args, **kw):
    """does something"""

    try:
        obj = args[2]
        obj.append(kw['kwa'])
        mutable_shared_state[0] += 1
        try:
            if obj.is_ready:
                x = 2 / 0
        except Exception:
            raise Exception()

    except:
        pass


some_list = [0, 1, 2, 3]
try:
    someList[0] += 3
except NameError:
    some_stupid_function(some_list, 1, "o", 3, kwo=10)
    pass
except:
    pass
