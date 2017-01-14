""""""

# Standard library modules.
import re
from distutils.version import LooseVersion

# Third party modules.
from bs4 import BeautifulSoup

# Local modules.
from pymontecarlo_debian.core.versionparser import \
    WebpageVersionParser, PackageCloudVersionParser

# Globals and constants variables.

WEBPAGE_URL = 'http://montecarlomodeling.mcgill.ca/download/download.html'

class MCXrayWebpageVersionParser(WebpageVersionParser):

    PATTERN = r'MCXRayLite_v([0-9.]*).zip$'

    def __init__(self):
        super().__init__(WEBPAGE_URL)

    def _parse_webpage(self, content):
        soup = BeautifulSoup(content, "html.parser")

        versions = []
        for a in soup.find_all('a'):
            match = re.match(self.PATTERN, a['href'])
            if not match:
                continue

            version = LooseVersion(match.group(1))

            versions.append(version)

        if not versions:
            return None

        return max(versions)

class MCXrayPackageCloudVersionParser(PackageCloudVersionParser):

    def __init__(self, api_token):
        super().__init__(api_token, 'ppinard', 'pymontecarlo', 'mcxray-lite')
