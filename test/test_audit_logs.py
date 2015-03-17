from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest

class TestAuditLogs(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_first_2_logs(self):
        logs_list = self.space.audit_log_management.audit_logs.get(
                        paging={'start': 0, 'limit': 2})
        print(len(logs_list))
        assert len(logs_list) == 2, "Not enough logs on Space"

    def test_get_next_2_logs(self):
        logs_list = self.space.audit_log_management.audit_logs.get(
                        paging={'start': 2, 'limit': 2})
        print(len(logs_list))
        assert len(logs_list) == 2, "Not enough logs on Space"

    def test_get_2_logs(self):
        logs_list = self.space.audit_log_management.audit_logs.get(
                        paging={'start': 0, 'limit': 2})
        print(len(logs_list))
        assert len(logs_list) == 2, "Not enough logs on Space"

        for log in logs_list:
            log_detail = log.get()
            assert log_detail.userName
