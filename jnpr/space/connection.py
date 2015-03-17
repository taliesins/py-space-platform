"""
This module defines the Connection class.
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import requests
import logging


class Connection(object):
    """ Creates a connection to Space Platform mimicking a GUI login.
    This class is **not** thread-safe. It is up to the users of the class to
    ensure thread safety. The ``rest.Space`` class uses this class for
    supporting session-based connections to Junos Space. Thread-safety
    requirements are met by that class.
    """

    def __init__(self,
                 homeurl,
                 username=None,
                 password=None,
                 cert=None,
                 our_ip=None):
        self._logger = logging.getLogger('root')
        self.homeurl = homeurl + '/mainui'
        self.authurl = homeurl + '/mainui/j_security_check'
        self.session = None

        if username is not None:
            if password is None:
                raise ValueError('password is mandatory along with username')
            if cert is not None:
                raise ValueError('You must provide only one of username+password or cert')
        else:
            if password is not None:
                raise ValueError('password is valid only along with username')
            if cert is None:
                raise ValueError('You must provide one of username+password or cert')

        self.username = username
        self.password = password
        self.our_ip = our_ip

        self.cert = cert

        self._logger.debug("Connection: Initiating login to %s", self.homeurl)
        self.login()

    def login(self):
        """ Login to Space """

        self.session = requests.Session()
        sess = self.session
        if self.our_ip is None:
            resp = sess.get(self.homeurl, cert=self.cert, verify=False)
            #self._logger.debug(resp.status_code)
            #self._logger.debug(resp.headers)
            #self._logger.debug(resp.text)

            # Extract the ipAddr and code variables embbed in the form validation code
            ip_addr_start_idx = resp.text.find("var ipAddr = ")
            if ip_addr_start_idx < 0:
                self.check_login_status()
                return

            ip_addr_end_idx = resp.text.find("\n", ip_addr_start_idx)
            ip_addr_line = resp.text[ip_addr_start_idx : ip_addr_end_idx]
            ip_addr_items = ip_addr_line.split("=", 2)
            ip_addr = ip_addr_items[1].strip("'; ").strip()

            #codeStartIdx = r.text.find("var code = ", ip_addr_end_idx);
            #codeEndIdx = r.text.find("\n", codeStartIdx);
            #codeLine = r.text[codeStartIdx : codeEndIdx]
            #codeItems = codeLine.split("=", 2);
            #code = codeItems[1].strip("'; ").strip();'''

            #form_username = self.username + '%' + code + '@' + ip_addr;
        else:
            resp = sess.get(self.homeurl, cert=self.cert, verify=False)
            ip_addr = self.our_ip

        form_username = self.username + '@' + ip_addr

        data = {
            "j_screen_username" : self.username,
            "j_username" : form_username,
            "j_password" : self.password
        }

        self._logger.debug(data)
        resp = sess.post(self.authurl, data=data, cert=self.cert, verify=False)

        #self._logger.debug(resp.status_code)
        #self._logger.debug(resp.headers)
        #self._logger.debug(resp.text)

        self.check_login_status()

    def is_logged_in(self):
        """ Checks if a login has been established """
        if self.session:
            return True
        else:
            return False

    def check_login_status(self):
        """ Check login-status """

        if not self.is_logged_in():
            raise Exception("Not logged in")

        resp = self.session.get(self.homeurl, verify=False)
        ip_addr_start_idx = resp.text.find("var ipAddr = ")
        if ip_addr_start_idx >= 0:
            raise Exception("Not in a logged-in session.")

    def get_session(self):
        """ Return the HTTP session object  """
        if self.is_logged_in():
            return self.session
        else:
            raise Exception("Not logged in")

    def logout(self):
        """ Logout from Space Server  """
        logout_url = self.homeurl + "/unsecured/logout.jsp"
        resp = self.session.get(logout_url, verify=False)
        #self._logger.debug(resp.status_code)
        #self._logger.debug(resp.headers)
        #self._logger.debug(resp.text)

        if resp.status_code == 200:
            self.session = None

if __name__ == '__main__':

    import http.client
    http.client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    c = Connection('https://10.155.78.212', '', '',
                   cert=('/Users/rjoyce/ssl-cert-test/super.pem',
                         '/Users/rjoyce/ssl-cert-test/super_unencrypted.key'))
    r = c.session.get("https://10.155.78.212/api/space/user-management/users",
                      verify=False)
    print(r.text)
    c.logout()
