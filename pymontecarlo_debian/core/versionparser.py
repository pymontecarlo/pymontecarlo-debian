""""""

# Standard library modules.
from distutils.version import LooseVersion, Version

# Third party modules.
import requests

# Local modules.

# Globals and constants variables.

class VersionParser:

    def __init__(self, version):
        if version is not None and not isinstance(version, Version):
            version = LooseVersion(version)
        self.latest_version = version

class WebpageVersionParser(VersionParser):

    def __init__(self, url):
        content = self._retrieve_webpage(url)
        version = self._parse_webpage(content)
        super().__init__(version)

    def _retrieve_webpage(self, url):
        return requests.get(url).content

    def _parse_webpage(self, content):
        raise NotImplementedError

class PackageCloudVersionParser(VersionParser):

    def __init__(self, api_token, user, repos, package_name):
        packages = self._retrieve_packages(api_token, user, repos)
        version = self._parse_packages(packages, package_name)
        super().__init__(version)

    def _retrieve_packages(self, api_token, user, repos):
        url = 'https://packagecloud.io/api/v1/repos/{user}/{repos}/packages.json'
        url = url.format(user=user, repos=repos)
        return requests.get(url, auth=(api_token, '')).json()

    def _parse_packages(self, packages, package_name):
        versions = [LooseVersion(package['version'])
                    for package in packages
                    if package['name'] == package_name]

        if not versions:
            return None
        return max(versions)
