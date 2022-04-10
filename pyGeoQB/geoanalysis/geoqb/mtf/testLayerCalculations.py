import helper
import unittest

class MyTestCases(unittest.TestCase):

    def _test1(self):
        self.assertTrue( helper.test_something(self) )

    def test2(self):
        self.assertTrue( helper.test_something2(self) )


if __name__ == '__main__':
    unittest.main()




