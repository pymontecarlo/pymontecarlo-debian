#!/usr/bin/env python
""""""

# Standard library modules.
import os
import zipfile
import tempfile
from datetime import datetime
import shutil
import glob
import argparse

# Third party modules.
from debian.copyright import License, FilesParagraph

# Local modules.
from pymontecarlo_debian.core.debbuilder import DebBuilder
from pymontecarlo_debian.core.exeinfo import extract_exe_info
from pymontecarlo_debian.core.manpage import ManPage
from pymontecarlo_debian.core.desktopentry import DesktopEntry

# Globals and constants variables.

class MCXrayDebBuilder(DebBuilder):

    def __init__(self, zip_path):
        self._zip_path = zip_path

        # Exe info
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('McXRayLite.exe'):
                        break
                temp_file.write(z.read(filename))
                temp_file.close()
            self.exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        super().__init__(package='mcxray-lite',
                         fullname='MCX-Ray Lite',
                         version=self.exe_info['File version'], # dummy
                         maintainer='Raynald Gauvin',
                         maintainer_email='raynald.gauvin@mcgill.ca',
                         authors=['Raynald Gauvin', 'Pierre Michaud', 'Hendrix Demers'],
                         section='science',
                         short_description='Monte Carlo simulation of electron trajectory in solid',
                         long_description='MC X-Ray is a new Monte Carlo program that is an extension of the Monte Carlo programs Casino and Win X-Ray since it computes the complete x-ray spectra from the simulation of electron scattering in solids of various types of geometries. MC X-Ray allows up to 256 different regions in the materials having shape of spheres, cylinders and combinations of horizontal and vertical planes. All these regions can have a different composition. This program was written by Pierre Michaud under the supervision of Pr. Gauvin. Dr. Hendrix Demers improved and validated the x-ray spectrum computation of MC X-Ray.',
                         date=datetime.strptime(self.exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                         license='Private',
                         homepage='http://montecarlomodeling.mcgill.ca/software/mcxray/mcxray.html',
                         depends=['wine'])

    def _extract_zip(self, temp_dir, arch, *args, **kwargs):
        dirpath = os.path.join(temp_dir, 'zip')
        os.makedirs(dirpath)
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            for filename in z.namelist(): # Cannot use extract all, problem in zip
                z.extract(filename, dirpath)

    def _organize_files(self, temp_dir, arch, *args, **kwargs):
        # Copy zip content in share
        dst = os.path.join(temp_dir, 'usr', 'share', self.package)
        os.makedirs(dst, exist_ok=True)

        src_dir = os.path.join(temp_dir, 'zip')
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst)

        # Move documentation
        dst = os.path.join(temp_dir, 'usr', 'share', 'doc', self.package)
        os.makedirs(dst, exist_ok=True)

        for src in glob.iglob(os.path.join(temp_dir, 'usr', 'share',
                                           self.package, 'Documentations', '*')):
            shutil.copy(src, dst)
        shutil.rmtree(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'Documentations'))

        # Remove other architecture exe
        if arch == 'amd64':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'McXRayLite.exe'))
        elif arch == 'i386':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'McXRayLite_x64.exe'))

        # Remove Boost license (added to copyright file)
        shutil.rmtree(os.path.join(temp_dir, 'usr', 'share', self.package, 'licenses'))

        shutil.rmtree(src_dir)

    def _create_executable(self, temp_dir, arch, *args, **kwargs):
        if arch == 'amd64':
            filename = 'McXRayLite_x64.exe'
        elif arch == 'i386':
            filename = 'McXRayLite.exe'

        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/%s $@' % (self.package, filename))
        return lines

    def _write_executable(self, lines, temp_dir, arch, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'bin'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'bin', 'mcxray')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_man_page(self, temp_dir, arch, *args, **kwargs):
        return ManPage(package=self.package,
                       name='mcxray',
                       short_description=self.short_description,
                       synopsis='.B mcxray',
                       long_description=self.long_description,
                       see_also=self.homepage)

    def _create_desktop_entry(self, temp_dir, arch, *args, **kwargs):
        return DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                            name=self.fullname,
                            genericname=self.short_description,
                            nodisplay=False,
                            icon='mcxray',
                            exec_='mcxray',
                            terminal=False,
                            categories=['Science'])

    def _write_desktop_entry(self, entry, temp_dir, arch, *args, **kwargs):
        super()._write_desktop_entry(entry, temp_dir, arch, *args, **kwargs)

        # Copy icon
        dst_dir = os.path.join(temp_dir, 'usr', 'share', 'icons',
                               'hicolor', '48x48', 'apps')
        os.makedirs(dst_dir, exist_ok=True)

        src = os.path.join(os.path.dirname(__file__), 'McXRayLite.png')
        dst = os.path.join(dst_dir, 'mcxray.png')
        shutil.copy(src, dst)

    def _create_control(self, temp_dir, arch, *args, **kwargs):
        control = super()._create_control(temp_dir, arch, *args, **kwargs)
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
    parser = argparse.ArgumentParser(description='Create deb for MCXray')

    parser.add_argument('filepath', help='Path to ZIP containing MCXray')
    parser.add_argument('-a', '--arch', choices=('amd64', 'i386'), required=True,
                        help='Architecture')
    parser.add_argument('-o', '--output', help='Path to output directory')

    args = parser.parse_args()

    filepath = args.filepath

    outputdir = args.output
    if not outputdir:
        outputdir = os.path.dirname(filepath)

    arch = args.arch

    debbuilder = MCXrayDebBuilder(filepath)
    debbuilder.build(outputdir, arch=arch)

if __name__ == '__main__':
    run()
