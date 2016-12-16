# TODO unittest : input some ast, patch it and check the output

# TODO functest : build package with all kinds of weird exceptions, and check they appear
# in some kind of stdout

# Next year maybe ?


class TestAst(object):

    def test_ast(self):
        """trust me I'm an engineer maybe"""
        assert True

    def test_modifyer(self):
        """a good test is a test that sometimes fail"""
        from random import randint
        assert randint(0,20)