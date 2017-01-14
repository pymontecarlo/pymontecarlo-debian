"""Base deb builder for programs"""

# Standard library modules.
import os
import textwrap
import gzip
from io import BytesIO, StringIO
import shutil
import tempfile
import abc

# Third party modules.
from debian.deb822 import Deb822
from debian.changelog import Changelog
from debian.copyright import Copyright, FilesParagraph, License

from deb_pkg_tools.package import build_package

# Local modules.

# Globals and constants variables.

def _format_debian_date(dt):
    s = dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    if dt.tzinfo is None:
        s += ' +0000'
    return s

class DebBuilder(metaclass=abc.ABCMeta):

    def __init__(self, package, fullname, version,
                 maintainer, maintainer_email, authors,
                 section, short_description, long_description, date, license,
                 homepage, priority='standard', depends=None, recommends=None):
        self.package = package
        self.fullname = fullname
        self.version = version.rstrip('-1')
        self.maintainer = maintainer
        self.maintainer_email = maintainer_email
        self.authors = tuple(authors)
        self.section = section
        self.short_description = short_description
        self.long_description = long_description
        self.date = date
        self.license = license
        self.homepage = homepage
        self.priority = priority
        self.depends = tuple(depends or ())
        self.recommends = tuple(recommends or ())

    def _create_temp_dir(self, *args, **kwargs):
        return tempfile.mkdtemp()

    def _create_control(self, temp_dir, *args, **kwargs):
        wrapper = textwrap.TextWrapper(initial_indent=' ',
                                       subsequent_indent=' ',
                                       width=80)
        description = \
            self.short_description + '\n' + wrapper.fill(self.long_description)

        fields = {'Package': self.package,
                  'Version': self.version + '-1',
                  'Section': self.section,
                  'Priority': self.priority,
                  'Architecture': 'all',
                  'Depends': ', '.join(self.depends),
                  'Recommends': ', '.join(self.recommends),
                  'Maintainer': '{0} <{1}>'.format(self.maintainer, self.maintainer_email),
                  'Description': description,
                  'Homepage': self.homepage,
                  }
        control = Deb822()
        control.update(fields)
        return control

    def _write_control(self, control, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        control_filepath = os.path.join(temp_dir, 'DEBIAN', 'control')
        with open(control_filepath, 'wb') as fp:
            control.dump(fp)

    def _create_preinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "install" ] ; then')
        lines.append('  echo "Installing %s"' % self.package)
        lines.append('fi')
        lines.append('')
        lines.append('if [ "$1" = "upgrade" ] ; then')
        lines.append('  echo "Upgrading %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_preinst(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'preinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postinst(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "configure" ] ; then')
        lines.append('  echo "Configuring %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postinst(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postinst')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_prerm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "remove" ] ; then')
        lines.append('  echo "Removing %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_prerm(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'prerm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_postrm(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('set -e')
        lines.append('if [ "$1" = "purge" ] ; then')
        lines.append('  echo "Purging %s"' % self.package)
        lines.append('fi')
        lines.append('exit 0')
        return lines

    def _write_postrm(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'DEBIAN', 'postrm')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    @abc.abstractmethod
    def _create_man_page(self, temp_dir, *args, **kwargs):
        raise NotImplementedError

    def _write_man_page(self, manpage, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'man', 'man1'),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'man', 'man1',
                                '%s.1.gz' % manpage.name)
        with gzip.open(filepath, 'wb', 9) as z:
            buf = StringIO()
            manpage.write(buf)
            z.write(buf.getvalue().encode('ascii'))

    @abc.abstractmethod
    def _create_desktop_entry(self, temp_dir, *args, **kwargs):
        raise NotImplementedError

    def _write_desktop_entry(self, entry, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'applications'),
                    exist_ok=True)

        name = os.path.basename(entry.exec_)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'applications',
                                '%s.desktop' % name)
        with open(filepath, 'wt') as fp:
            entry.write(fp)

    def _create_copyright(self, temp_dir, *args, **kwargs):
        copyrightobj = Copyright()
        copyrightobj.header.upstream_name = self.fullname
        copyrightobj.header.upstream_contact = (self.maintainer, self.maintainer_email)

        copyright = '{0:d} {1}'.format(self.date.year, ', '.join(self.authors))
        license = License('Custom', self.license)
        paragraph = FilesParagraph.create('*', copyright, license)
        copyrightobj.add_files_paragraph(paragraph)

        return copyrightobj

    def _write_copyright(self, copyright, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'doc', self.package),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self.package, 'copyright')
        with open(filepath, 'w') as fp:
            copyright.dump(fp)

    def _create_changelog(self, temp_dir, *args, **kwargs):
        changelog = Changelog()
        changelog.new_block()
        changelog.set_version(self.version)
        changelog.set_package(self.package)
        changelog.set_distributions('all')
        changelog.set_urgency('low')
        changelog.set_author('{0} <{1}>'.format(self.maintainer, self.maintainer_email))
        changelog.set_date(_format_debian_date(self.date))
        changelog.add_change('  * Release of %s' % self.version)
        return changelog

    def _write_changelog(self, changelog, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'doc', self.package),
                    exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'share', 'doc',
                                self.package, 'changelog.Debian.gz')
        with gzip.open(filepath, 'wb', 9) as z:
            buf = BytesIO()
            buf.write(changelog.__bytes__())
            z.write(buf.getvalue())

    def _build_deb(self, temp_dir, outputdir, *args, **kwargs):
        os.makedirs(outputdir, exist_ok=True)
        build_package(temp_dir, outputdir)

    def _cleanup(self, temp_dir, *args, **kwargs):
        shutil.rmtree(temp_dir)

    def build(self, outputdir, *args, **kwargs):
        try:
            temp_dir = self._create_temp_dir(*args, **kwargs)
            self._build(temp_dir, *args, **kwargs)
            self._build_deb(temp_dir, outputdir)
        finally:
            self._cleanup(temp_dir)

    def _build(self, temp_dir, *args, **kwargs):
        control = self._create_control(temp_dir, *args, **kwargs)
        self._write_control(control, temp_dir, *args, **kwargs)

        lines = self._create_preinst(temp_dir, *args, **kwargs)
        self._write_preinst(lines, temp_dir, *args, **kwargs)

        lines = self._create_postinst(temp_dir, *args, **kwargs)
        self._write_postinst(lines, temp_dir, *args, **kwargs)

        lines = self._create_prerm(temp_dir, *args, **kwargs)
        self._write_prerm(lines, temp_dir, *args, **kwargs)

        copyright = self._create_postrm(temp_dir, *args, **kwargs)
        self._write_postrm(copyright, temp_dir, *args, **kwargs)

        lines = self._create_copyright(temp_dir, *args, **kwargs)
        self._write_copyright(lines, temp_dir, *args, **kwargs)

        changelog = self._create_changelog(temp_dir, *args, **kwargs)
        self._write_changelog(changelog, temp_dir, *args, **kwargs)
