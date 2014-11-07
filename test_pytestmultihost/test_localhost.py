import getpass
import pytest
from subprocess import CalledProcessError

import pytest_multihost

try:
    from paramiko import AuthenticationException
except ImportError:
    class AuthenticationException(Exception):
        """Never raised"""

@pytest.fixture(scope='class')
def multihost(request):
    mh = pytest_multihost.make_fixture(
        request,
        descriptions=[
            {
                'hosts': {
                    'local': 1,
                },
            },
        ],
        _confdict={
            'ssh_username': getpass.getuser(),
            'domains': [
                {
                    'name': 'localdomain',
                    'hosts': [
                        {
                            'name': 'localhost',
                            'external_hostname': 'localhost',
                            'ip': '127.0.0.1',
                            'role': 'local',
                        },
                    ],
                },
            ],
        },
    )
    mh.host = mh.config.domains[0].hosts[0]
    return mh.install()


class TestLocalhost(object):
    def test_localhost(self, multihost):
        host = multihost.host
        try:
            echo = host.run_command(['echo', 'hello', 'world'])
        except (AuthenticationException, CalledProcessError):
            print (
                'Cannot login to %s using default SSH key (%s), user %s. '
                'You might want to add your own key '
                'to ~/.ssh/authorized_keys.') % (
                    host.external_hostname,
                    host.ssh_key_filename,
                    getpass.getuser())
            raise
        assert echo.stdout_text == 'hello world\n'