import unittest
import ciscoios


class TestStringMethods(unittest.TestCase):

  def test_get_switches(self):
      ios = ciscoios.CiscoIOS()
      self.assertEqual('foo'.upper(), 'FOO')

  # def test_isupper(self):
  #     self.assertTrue('FOO'.isupper())
  #     self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()
