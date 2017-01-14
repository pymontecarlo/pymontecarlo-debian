""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_debian.core.versionparser import PackageCloudVersionParser

# Globals and constants variables.

class MonacoPackageCloudVersionParser(PackageCloudVersionParser):

    def __init__(self, api_token):
        super().__init__(api_token, 'ppinard', 'pymontecarlo', 'monaco')
