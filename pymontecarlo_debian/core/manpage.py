""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class ManPage(object):

    def __init__(self, package, name, short_description='', synopsis='',
                 long_description='', see_also=''):
        self.package = package
        self.name = name
        self.short_description = short_description
        self.synopsis = synopsis
        self.long_description = long_description
        self.see_also = see_also

    def write(self, fp):
        def e(s):
            return s.replace('-', '\\-')

        lines = []
        lines.append('.TH %s 1 "" "" %s' % (e(self.name), e(self.package)))
        lines.append('')
        lines.append('.SH NAME')
        lines.append('%s \\- %s' % (e(self.name), e(self.short_description)))
        if self.synopsis:
            lines.append('')
            lines.append('.SH SYNOPSIS')
            lines.append('%s' % e(self.synopsis))
        if self.long_description:
            lines.append('')
            lines.append('.SH DESCRIPTION')
            lines.append(e(self.long_description))
        if self.see_also:
            lines.append('')
            lines.append('.SH SEE ALSO')
            lines.append('%s' % e(self.see_also))
        fp.write('\n'.join(lines))