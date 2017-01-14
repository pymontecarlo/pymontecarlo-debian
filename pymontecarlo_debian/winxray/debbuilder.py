#!/usr/bin/env python
""""""

# Standard library modules.
import os
import zipfile
import tempfile
from datetime import datetime
import shutil
import argparse

# Third party modules.

# Local modules.
from pymontecarlo_debian.core.debbuilder import DebBuilder
from pymontecarlo_debian.core.exeinfo import extract_exe_info
from pymontecarlo_debian.core.manpage import ManPage
from pymontecarlo_debian.core.desktopentry import DesktopEntry

# Globals and constants variables.

class WinXRayDebBuilder(DebBuilder):

    def __init__(self, zip_path):
        self._zip_path = zip_path

        # Exe info
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('WinXRay.exe'):
                        break
                temp_file.write(z.read(filename))
                temp_file.close()
            self.exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        super().__init__(package='winxray',
                         fullname='WinXRay',
                         version=self.exe_info['File version'], # dummy
                         maintainer='Hendrix Demers',
                         maintainer_email='hendrix.demers@mail.mcgill.ca',
                         authors=['H. Demers', 'P. Horny', 'R. Gauvin', 'E. Lifshin'],
                         section='science',
                         short_description='Monte Carlo simulation of electron trajectory in solid',
                         long_description='This new Monte Carlo programs, Ray, is a extension of the well known Monte Carlo program CASINO, which includes statistical distributions for the backscattered electrons, trapped electrons, energy loss and phi rho z curves for X-ray. The new added features in Ray are: the complete simulation of the X-ray spectrum, the charging effect for insulating specimen.',
                         date=datetime.strptime(self.exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                         license='This program is for educational and scientific use only. All commercial applications concerning this program are prohibited without a written agreement with the authors. We claim no responsibility and liability concerning the technical predictions of this programs.\nIn all publications using the results of this program, the complete references to Win X-Ray and the authors must be include in the paper.  And if you send us the paper, we will be pleasure to see want use you have made of the program.',
                         homepage='http://montecarlomodeling.mcgill.ca/software/winxray/winxray.html',
                         depends=['wine'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            z.extractall(temp_dir)

    def _organize_files(self, temp_dir, *args, **kwargs):
        # Copy files to share
        def _find(name, path):
            for root, _dirs, files in os.walk(path):
                if name in files:
                    return os.path.join(root, name)

        dst_dir = os.path.join(temp_dir, 'usr', 'share', self.package)
        os.makedirs(dst_dir, exist_ok=True)

        src_dir = os.path.dirname(_find('WinXRay.exe', temp_dir))
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst_dir)

        # Copy icon
        dst_dir = os.path.join(temp_dir, 'usr', 'share', 'icons',
                               'hicolor', '48x48', 'apps')
        os.makedirs(dst_dir, exist_ok=True)

        src = os.path.join(os.path.dirname(__file__), 'WinXRay.png')
        dst = os.path.join(dst_dir, 'winxray.png')
        shutil.copy(src, dst)

        # Remove license file (already in copyright)
        os.remove(os.path.join(temp_dir, 'usr', 'share', self.package,
                               'Help', 'License.txt'))

        # Remove temporary directory
        shutil.rmtree(src_dir)

    def _create_executable(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/WinXRay.exe $@' % self.package)
        return lines

    def _write_executable(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'bin'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'bin', 'winxray')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_man_page(self, temp_dir, *args, **kwargs):
        return ManPage(package=self.package,
                       name='winxray',
                       short_description=self.short_description,
                       synopsis='.B winxray',
                       long_description=self.long_description,
                       see_also=self.homepage)

    def _create_desktop_entry(self, temp_dir, *args, **kwargs):
        return DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                            name=self.fullname,
                            genericname=self.short_description,
                            nodisplay=False,
                            icon='winxray',
                            exec_='winxray',
                            terminal=False,
                            categories=['Science'])

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._organize_files(temp_dir, *args, **kwargs)

        lines = self._create_executable(temp_dir, *args, **kwargs)
        self._write_executable(lines, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        entry = self._create_desktop_entry(temp_dir, *args, **kwargs)
        self._write_desktop_entry(entry, temp_dir, *args, **kwargs)

        super()._build(temp_dir, *args, **kwargs)

def run():
    parser = argparse.ArgumentParser(description='Create deb for WinXRay')

    parser.add_argument('filepath', help='Path to ZIP containing WinXRay')
    parser.add_argument('-o', '--output', help='Path to output directory')

    args = parser.parse_args()

    filepath = args.filepath

    outputdir = args.output
    if not outputdir:
        outputdir = os.path.dirname(filepath)

    debbuilder = WinXRayDebBuilder(filepath)
    debbuilder.build(outputdir)

if __name__ == '__main__':
    run()
