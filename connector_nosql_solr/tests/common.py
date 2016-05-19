import mock
from contextlib import contextmanager
from openerp.tests.common import TransactionCase


class SunburntMock(object):
    """ Used to simulate the calls to SolR
    For a call (request) to SolR, returns a stored
    response.
    """

    def __init__(self):
        self._calls = []
        self.location = None

    def add(self, datas, chunk):
        self._calls.append(('add', chunk, datas))
        return True

    def commit(self):
        self._calls.append(('commit'))
        return True

    def delete(self, datas):
        self._calls.append(('delete', datas))
        return True


@contextmanager
def mock_api():
    sunburnt_mock = SunburntMock()

    def get_mock_interface(location):
        sunburnt_mock.location = location
        return sunburnt_mock

    with mock.patch('sunburnt.SolrInterface', get_mock_interface):
        yield sunburnt_mock


class SetUpSolrBase(TransactionCase):

    def setUp(self):
        super(SetUpSolrBase, self).setUp()
        self.backend = self.env.ref('connector_nosql_solr.backend_1')
