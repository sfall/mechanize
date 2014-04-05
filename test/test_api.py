import unittest


class ImportTests(unittest.TestCase):

    def test_import_all(self):
        # the following will raise an exception if __all__ contains undefined
        # classes
        from mechanize import __all__ as things
        for thing in things:
            exec('from mechanize import '+thing)


if __name__ == "__main__":
    unittest.main()
