"""Casino2 debian builder"""

# Standard library modules.
import os
import zipfile
import tempfile
from datetime import datetime
import shutil
import argparse

# Third party modules.
from debian.copyright import FilesParagraph, License

# Local modules.
from pymontecarlo_debian.core.debbuilder import DebBuilder
from pymontecarlo_debian.core.manpage import ManPage
from pymontecarlo_debian.core.desktopentry import DesktopEntry
from pymontecarlo_debian.core.exeinfo import extract_exe_info

# Globals and constants variables.

class Casino2DebBuilder(DebBuilder):

    def __init__(self, zip_path):
        self._zip_path = zip_path

        # Exe info
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('wincasino2.exe'):
                        break
                temp_file.write(z.read(filename))
                temp_file.close()
            self.exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        super().__init__(package='casino2',
                         fullname='Casino 2',
                         version=self.exe_info['File version'], # dummy
                         maintainer='Hendrix Demers',
                         maintainer_email='hendrix.demers@mail.mcgill.ca',
                         authors=['D. Drouin', 'A.R. Couture', 'R. Gauvin',
                                  'P. Hovington', 'P. Horny', 'H. Demers',
                                  'D. Joly', 'P. Drouin', 'N. Poirier-Demers'],
                         section='science',
                         short_description='Monte Carlo simulation of electron trajectory in solid',
                         long_description='The CASINO acronym has been derived from the words "monte CArlo SImulation of electroN trajectory in sOlids". This program is a Monte Carlo simulation of electron trajectory in solid specially designed for low beam interaction in a bulk and thin foil. This complex single scattering Monte Carlo program is specifically designed for low energy beam interaction and can be used to generate many of the recorded signals (X-rays and backscattered electrons) in a scanning electron microscope. This program can also be efficiently used for all of the accelerated voltage found on a field emission scanning electron microscope(0.1 to 30 KeV).',
                         date=datetime.strptime(self.exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                         license='We clain no responsibility and liability concerning the technical predictions of this program. In all publications using the results of this program, the complete references to CASINO must be include in the paper.',
                         homepage='http://www.gel.usherbrooke.ca/casino/',
                         depends=['wine'])

    def _extract_zip(self, temp_dir, arch, *args, **kwargs):
        dirpath = os.path.join(temp_dir, 'zip')
        os.makedirs(dirpath)
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            for filename in z.namelist(): # Cannot use extract all, problem in zip
                z.extract(filename, dirpath)

    def _organize_files(self, temp_dir, arch, *args, **kwargs):
        # Copy files to share
        dst_dir = os.path.join(temp_dir, 'usr', 'share', self.package)
        os.makedirs(dst_dir, exist_ok=True)

        src_dir = os.path.join(temp_dir, 'zip')
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst_dir)

        # Remove exe from other architecture
        if arch == 'amd64':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'wincasino2.exe'))
        elif arch == 'i386':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'wincasino2_64.exe'))

        # Remove Boost license (added to copyright file)
        shutil.rmtree(os.path.join(temp_dir, 'usr', 'share', self.package, 'licenses'))

        # Copy icon
        dst_dir = os.path.join(temp_dir, 'usr', 'share', 'icons',
                               'hicolor', '48x48', 'apps')
        os.makedirs(dst_dir, exist_ok=True)

        src = os.path.join(os.path.dirname(__file__), 'wincasino2.png')
        dst = os.path.join(dst_dir, 'casino2.png')
        shutil.copy(src, dst)

        # Remove temporary directory
        shutil.rmtree(src_dir)

    def _create_executable(self, temp_dir, arch, *args, **kwargs):
        if arch == 'amd64':
            filename = 'wincasino2_64.exe'
        elif arch == 'i386':
            filename = 'wincasino2.exe'

        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/%s $@' % (self.package, filename))
        return lines

    def _write_executable(self, lines, temp_dir, arch, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'bin'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'bin', 'casino2')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_man_page(self, temp_dir, arch, *args, **kwargs):
        return ManPage(package=self.package,
                       name='casino2',
                       short_description=self.short_description,
                       synopsis='.B casino2',
                       long_description=self.long_description,
                       see_also=self.homepage)

    def _create_desktop_entry(self, temp_dir, arch, *args, **kwargs):
        return DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                            name=self.fullname,
                            genericname=self.short_description,
                            nodisplay=False,
                            icon='casino2',
                            exec_='casino2',
                            terminal=False,
                            categories=['Science'])

    def _create_control(self, temp_dir, arch, *args, **kwargs):
        control = super()._create_control(temp_dir, *args, **kwargs)
        control['Architecture'] = arch
        return control

    def _create_copyright(self, temp_dir, arch, *args, **kwargs):
        copyrightobj = super()._create_copyright(temp_dir, arch, *args, **kwargs)

        # Add Boost license
        copyright = 'August 17th, 2003'
        synopsis = """
Permission is hereby granted, free of charge, to any person or organization
obtaining a copy of the software and accompanying documentation covered by
this license (the "Software") to use, reproduce, display, distribute,
execute, and transmit the Software, and to prepare derivative works of the
Software, and to permit third-parties to whom the Software is furnished to
do so, all subject to the following:

The copyright notices in the Software and this entire statement, including
the above license grant, this restriction and the following disclaimer,
must be included in all copies of the Software, in whole or in part, and
all derivative works of the Software, unless such copies or derivative
works are solely in the form of machine-executable object code generated by
a source language processor.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
        """
        license = License('Boost Software License - Version 1.0', synopsis)
        paragraph = FilesParagraph.create('*', copyright, license)
        copyrightobj.add_files_paragraph(paragraph)

        return copyrightobj

    def _build(self, temp_dir, arch, *args, **kwargs):
        self._extract_zip(temp_dir, arch, *args, **kwargs)

        self._organize_files(temp_dir, arch, *args, **kwargs)

        lines = self._create_executable(temp_dir, arch, *args, **kwargs)
        self._write_executable(lines, temp_dir, arch, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, arch, *args, **kwargs)
        self._write_man_page(manpage, temp_dir, arch, *args, **kwargs)

        entry = self._create_desktop_entry(temp_dir, arch, *args, **kwargs)
        self._write_desktop_entry(entry, temp_dir, arch, *args, **kwargs)

        super()._build(temp_dir, arch, *args, **kwargs)

    def build(self, outputdir, arch, *args, **kwargs):
        if arch not in ['amd64', 'i386']:
            raise ValueError('Invalid architecture: amd64 or i386')
        super().build(outputdir, arch, *args, **kwargs)

def run():
    parser = argparse.ArgumentParser(description='Create deb for Casino 2')

    parser.add_argument('filepath', help='Path to ZIP containing Casino 2')
    parser.add_argument('-a', '--arch', choices=('amd64', 'i386'), required=True,
                        help='Architecture')
    parser.add_argument('-o', '--output', help='Path to output directory')

    args = parser.parse_args()

    filepath = args.filepath

    outputdir = args.output
    if not outputdir:
        outputdir = os.path.dirname(filepath)

    arch = args.arch

    debbuilder = Casino2DebBuilder(filepath)
    debbuilder.build(outputdir, arch=arch)

if __name__ == '__main__':
    run()
