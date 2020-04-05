from packaging import version
from pathlib import Path
import subprocess
import os
import time
import wget
import winreg
from zipfile import ZipFile
import win32com.client as wc
import site
import shutil

_MS_CPP_REDISTRIBUTABLE_PACKAGES_URL = 'https://download.microsoft.com/download/1/6/5/' + \
    '165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x64.exe'
_CAPITAL_API_PACKAGE_URL = 'https://www.capital.com.tw/Service2/download/api_zip/CapitalAPI_%s.zip'


class Helper:
    __stdout = ''
    __stderr = ''
    __url = ''
    _require_ver = None
    _current_ver = None
    _package_work_dir = None
    _download_file = ''

    @property
    def version(self):
        return self._current_ver

    @property
    def stdout(self):
        return self.__stdout

    @property
    def stderr(self):
        return self.__stderr

    def __init__(self, require_ver, url, work_dir):
        self.__url = url
        self._require_ver = version.parse(require_ver)
        self._package_work_dir = Path(work_dir).expanduser()

        self._get_curr_ver()
        self._package_work_dir.mkdir(parents=True, exist_ok=True)
        self.__download_target_file()

    def __download_target_file(self):
        self._download_file = Path(self._package_work_dir.as_posix() + '/' + wget.filename_from_url(self.__url))

        if not self._download_file.exists():
            wget.download(self.__url, self._download_file.as_posix())

    def _powershell_exec(self, exe, args_list, admin=False):
        exec_cmd = []

        if admin:
            exec_cmd = [
                'powershell.exe', 'Start-Process',
                '-FilePath', '"' + exe + '"',
                '-ArgumentList', ','.join(list(map(lambda i: '"%s"' % i, args_list))),
                '-Wait', '-Verb', 'RunAs'
            ]
        else:
            exec_cmd = [
                'powershell.exe', 'Start-Process',
                '-FilePath', '"' + exe + '"',
                '-ArgumentList', '"' + ','.join(args_list) + '"',
                '-Wait',
                '-Passthru'
            ]
        complete = subprocess.run(exec_cmd, shell=True, capture_output=True)

        if complete.returncode != 0:
            self.__stdout = complete.stdout
            self.__stderr = complete.stderr
            return False

        return True

    def _get_curr_ver(self):
        raise NotImplementedError()

    def install(self):
        raise NotImplementedError()

    def uninstall(self):
        raise NotImplementedError()

    def check_version(self):
        if self._current_ver != self._require_ver:
            return False

        return True

    def auto_install(self):
        if self._current_ver == version.parse('0.0.0.0'):
            self.install()

        if not self.check_version():
            self.uninstall()
            self.install()


class VcredistHelper(Helper):
    __dll_file = ''

    def __init__(self, require_ver, work_dir):
        super(VcredistHelper, self).__init__(require_ver,
                                             _MS_CPP_REDISTRIBUTABLE_PACKAGES_URL,
                                             work_dir)

    def _get_curr_ver(self):
        try:
            # version format: 10.0.40219.325
            keyname = r'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\10.0\VC\VCRedist\x64'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keyname)
            self._current_ver = version.parse(winreg.QueryValueEx(key, 'Version')[0].strip('v'))
        except FileNotFoundError:
            self._current_ver = version.parse('0.0.0.0')

    def install(self):
        if not self._powershell_exec(self._download_file.as_posix(), ['/passive']):
            raise WindowsError('Install Microsoft C++ Redistributable package failure!\n' + self.stderr)
        self._get_curr_ver()

    def uninstall(self):
        if not self._powershell_exec(self._download_file.as_posix(), ['/uninstall /q']):
            raise WindowsError('Uninstall Microsoft C++ Redistributable package failure!\n' + self.stderr)
        self._get_curr_ver()


class CapitalAPIHelper(Helper):
    __dll_file = ''

    @property
    def api_path(self):
        return self.__dll_file.as_posix()

    def __init__(self, require_ver, work_dir):
        super(CapitalAPIHelper, self).__init__(require_ver,
                                               _CAPITAL_API_PACKAGE_URL % require_ver,
                                               work_dir)

    def _get_curr_ver(self):
        try:
            # version format: 2.13.20
            keyname = r'CLSID\{54FE0E28-89B6-43A7-9F07-BE988BB40299}\InprocServer32'
            hkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, keyname)
            (reg_val, reg_id) = winreg.QueryValueEx(hkey, '')
            self.__dll_file = Path(reg_val)
            self._current_ver = version.parse(wc.Dispatch('Scripting.FileSystemObject').GetFileVersion(self.__dll_file))
        except FileNotFoundError:
            self._current_ver = version.parse('0.0.0.0')

        # if self._current_ver is None:
        #     self._current_ver = version.parse('0.0.0.0')

    def install(self):
        with ZipFile(self._download_file, 'r') as archive:
            for fname in archive.namelist():
                name_parts = fname.split('/')
                if name_parts[-2] == 'x64' and name_parts[-1].endswith('.dll'):
                    target_path = str(self._package_work_dir) + r'\\' + name_parts[-1]
                    with archive.open(fname, 'r') as cmpf, open(target_path, 'wb') as extf:
                        extf.write(cmpf.read())
            self.__dll_file = Path(self._package_work_dir.as_posix() + '/SKCOM.dll')

        # special case: if the path object "as_posix" method will return "/",
        #               but in powershell just can use "\",so using
        #               "expanduser" method instead of "as_posix" method
        if not self._powershell_exec('regsvr32', [self.__dll_file.expanduser()], True):
            raise WindowsError('Install Capital API failure!\n' + self.stderr)
        self._get_curr_ver()

    def uninstall(self):
        if self.__dll_file == '':
            return

        if not self.__dll_file.exists():
            return

        if not self._powershell_exec('regsvr32', ['/u', str(self.__dll_file)], True):
            raise WindowsError('Uninstall Capital API failure!\n' + self.stderr)

        self._get_curr_ver()
        # Clean the comtypes cache by document suggestion
        for pkg_dir in site.getsitepackages():
            if not pkg_dir.endswith('site-packages'):
                continue

            comtypes_dir = Path(pkg_dir + '\comtypes\gen')
            if comtypes_dir.exists() and comtypes_dir.is_dir():
                for child in comtypes_dir.iterdir():
                    if child.suffix == '.py':
                        os.remove(child)

                    if child.name == '__pycache__' and child.is_dir():
                        shutil.rmtree(child)
            return

        for child in self._package_work_dir.iterdir():
            if child.suffix == '.dll':
                os.remove(child)


# c = VcredistHelper('10.0.40219.325', '~/.liqueur')
# c = CapitalAPIHelper('2.13.20', '~/.liqueur')
# c.install()
# print(c.version)
# c.uninstall()
# print(c.version)
# c.install()
# print(c.version)
