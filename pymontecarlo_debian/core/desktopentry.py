""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class DesktopEntry(object):

    TYPE_APPLICATION = 'Application'
    TYPE_LINK = 'Link'
    TYPE_DIRECTORY = 'Directory'

    def __init__(self, type_, name, version=1.0, genericname=None,
                 nodisplay=None, comment=None, icon=None, hidden=None,
                 onlyshowin=None, notshowin=None, dbusactivatable=None,
                 tryexec=None, exec_=None, path=None, terminal=None,
                 actions=None, mimetype=None, categories=None, keywords=None,
                 startupnotify=None, startupwmclass=None, url=None):
        """
        Creates a desktop entry.
        """
        if type_ is self.TYPE_LINK and url is None:
            raise ValueError('url is required')

        self.type_ = type_
        self.name = name
        self.version = version
        self.genericname = genericname
        self.nodisplay = nodisplay
        self.comment = comment
        self.icon = icon
        self.hidden = hidden
        self.onlyshowin = tuple(onlyshowin or ())
        self.notshowin = tuple(notshowin or ())
        self.dbusactivatable = dbusactivatable
        self.tryexec = tryexec
        self.exec_ = exec_
        self.path = path
        self.terminal = terminal
        self.actions = actions
        self.mimetype = tuple(mimetype or ())
        self.categories = tuple(categories or ())
        self.keywords = tuple(keywords or ())
        self.startupnotify = startupnotify
        self.startupwmclass = startupwmclass
        self.url = url

    def write(self, fp):
        def b(v):
            return 'true' if v else 'false'
        def l(v):
            return ';'.join(map(lambda x: x.replace(';', '\\;'), v)) + ';'

        lines = []
        lines.append('[Desktop Entry]')
        lines.append('Type=%s' % self.type_)
        lines.append('Version=%s' % self.version)
        lines.append('Name=%s' % self.name)
        if self.genericname is not None:
            lines.append('GenericName=%s' % self.genericname)
        if self.comment is not None:
            lines.append('Comment=%s' % self.comment)
        if self.nodisplay is not None:
            lines.append('NoDisplay=%s' % b(self.nodisplay))
        if self.icon is not None:
            lines.append('Icon=%s' % self.icon)
        if self.hidden is not None:
            lines.append('Hidden=%s' % b(self.hidden))
        if self.onlyshowin:
            lines.append('OnlyShowIn=%s' % l(self.onlyshowin))
        if self.notshowin:
            lines.append('NotShowIn=%s' % l(self.notshowin))
        if self.dbusactivatable is not None:
            lines.append('DBusActivatable=%s' % b(self.dbusactivatable))
        if self.tryexec is not None:
            lines.append('TryExec=%s' % self.tryexec)
        if self.exec_ is not None:
            lines.append('Exec=%s' % self.exec_)
        if self.path is not None:
            lines.append('Path=%s' % self.path)
        if self.terminal is not None:
            lines.append('Terminal=%s' % b(self.terminal))
        if self.actions:
            lines.append('Actions=%s' % l(self.actions))
        if self.mimetype:
            lines.append('MimeType=%s' % l(self.mimetype))
        if self.categories:
            lines.append('Categories=%s' % l(self.categories))
        if self.keywords:
            lines.append('Keywords=%s' % l(self.keywords))
        if self.startupnotify is not None:
            lines.append('StartupNotify=%s' % b(self.startupnotify))
        if self.startupwmclass is not None:
            lines.append('StartupWMClass=%s' % self.startupwmclass)
        if self.url is not None:
            lines.append('URL=%s' % self.url)

        fp.write('\n'.join(lines))