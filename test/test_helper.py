import unittest
from packaging import version
from liqueur import VcredistHelper, VCREDIST_VER_REQUIRED, CapitalAPIHelper, DLL_VER_REQUIRED


class TestAutoPkgsInstallation(unittest.TestCase):
    def setUp(self):
        self.vcredist = VcredistHelper(VCREDIST_VER_REQUIRED, '~/.liqueur')
        self.capital_api = CapitalAPIHelper(DLL_VER_REQUIRED, '~/.liqueur')
        self.vcredist_ver = version.parse(VCREDIST_VER_REQUIRED)
        self.capital_api_ver = version.parse(DLL_VER_REQUIRED)
        self.blank_ver = version.parse('0.0.0.0')

    def test_vcredist_auto_install(self):
        if self.vcredist.version == self.blank_ver:
            self.assertIsNone(self.vcredist.auto_install())
            self.assertEqual(self.vcredist.version, self.vcredist_ver)
            self.assertIsNone(self.vcredist.uninstall())
            self.assertEqual(self.vcredist.version, self.blank_ver)
            self.assertIsNone(self.vcredist.install())
            self.assertEqual(self.vcredist.version, self.vcredist_ver)
        else:
            self.assertIsNone(self.vcredist.uninstall())
            self.assertEqual(self.vcredist.version, self.blank_ver)

            self.assertIsNone(self.vcredist.install())
            self.assertEqual(self.vcredist.version, self.vcredist_ver)
            self.assertIsNone(self.vcredist.uninstall())
            self.assertEqual(self.vcredist.version, self.blank_ver)
            self.assertIsNone(self.vcredist.auto_install())
            self.assertEqual(self.vcredist.version, self.vcredist_ver)

    def test_capital_api_auto_install(self):
        if self.capital_api.version == self.blank_ver:
            self.assertIsNone(self.capital_api.auto_install())
            self.assertEqual(self.capital_api.version, self.capital_api_ver)
            self.assertIsNone(self.capital_api.uninstall())
            self.assertEqual(self.capital_api.version, self.blank_ver)
            self.assertIsNone(self.capital_api.install())
            self.assertEqual(self.capital_api.version, self.capital_api_ver)
        else:
            self.assertIsNone(self.capital_api.uninstall())
            self.assertEqual(self.capital_api.version, self.blank_ver)
            self.assertIsNone(self.capital_api.install())
            self.assertEqual(self.capital_api.version, self.capital_api_ver)
            self.assertIsNone(self.capital_api.uninstall())
            self.assertEqual(self.capital_api.version, self.blank_ver)
            self.assertIsNone(self.capital_api.auto_install())
            self.assertEqual(self.capital_api.version, self.capital_api_ver)


if __name__ == '__main__':
    unittest.main()
