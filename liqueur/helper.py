from packaging import version
import site
import re
import os
import winreg

_MS_CPP_REDISTRIBUTABLE_PACKAGES_REQUIRED_VER = 'v10.0.40219.325'
_MS_CPP_REDISTRIBUTABLE_PACKAGES_URL = 'https://download.microsoft.com/download/1/6/5/' + \
    '165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x64.exe'


class DllHelper:
    __curr_pkg_ver = '0.0.0.0'
    __required_pkg_ver = version.parse(_MS_CPP_REDISTRIBUTABLE_PACKAGES_REQUIRED_VER)

    @staticmethod
    def powershell_exec(cmd_list, admin=True):
        if not isinstance(cmd_list, list):
            raise TypeError('TODO')

        exec_cmd = ['powershell.exe', 'Start-Process', '-FilePath', cmd_list[0]]
        if len(cmd_list) > 1:
            args = ','.join(list(map(lambda i: '"%s"' % i, tokens[1:])))
            exec_cmd.append('-ArgumentList', args)

        if admin:
            exec_cmd.append('-Verb')
            exec_cmd.append('RunAs')
        else:
            exec_cmd.append('-NoNewWindow')
            exec_cmd.append('-Wait')

        completed = subprocess.run(exec_cmd, stdout=subprocess.PIPE)
        if completed.returncode == 0:
            return completed.stdout.decode('cp950')

        return None

    @staticmethod
    def cmd_exec(cmd_list):
        exec_cmd = ['cmd', '/C'] + cmd_list

        completed = subprocess.run(exec_cmd, stdout=subprocess.PIPE)
        if completed.returncode == 0:
            return completed.stdout.decode('cp950')

        return None

    def __folder_exist(self, folder_path):
        full_folder_path = os.path.expanduser(folder_path)
        if not os.path.isdir(full_folder_path):
            os.makedirs(full_folder_path)

        return os.path.realpath(full_folder_path)

    def __download_file(self, url, folder_path):
        folder_path = self.__folder_exist(folder_path)
        file_path = r'%s\%s' % (folder_path, url.split('/')[-1])

        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                f.flush()

        return file_path

    def __init__(self):
        try:
            keyname = r'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\10.0\VC\VCRedist\x64'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keyname)
            ver = winreg.QueryValueEx(key, 'Version')[0]

            if not re.match(r'v(\d+\.){3}\d+', ver):
                ver = 'v0.0.0.0'
        except FileNotFoundError:
            ver = 'v0.0.0.0'

        self.__curr_pkg_ver = version.parse(ver)

    def insert_required_package(self):
        if self.__curr_pkg_ver >= self.__required_pkg_ver:
            return

        file_path = self.__download_file(_MS_CPP_REDISTRIBUTABLE_PACKAGES_URL, '~/.tmp')
        DllHelper.powershell_exec([file_path + r' setup /passive'])

        cmd_args = ['tasklist', '/fi', 'imagename eq vcredist_x64.exe', '/fo', 'csv']

        while DllHelper.cmd_exec(cmd_args).count('\r\n') == 2:
            time.sleep(0.5)

        os.remove(file_path)

    def dump(self):
        print('Current c++ redistributable package version: %s' % self.__curr_pkg_ver)


help = DllHelper()
help.dump()
