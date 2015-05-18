import unittest,dynamicIp

class DynamicIpTestCase(unittest.TestCase):

    def setUp(self):
        self.app = dynamicIp.app.test_client()

    def tearDown(self):
        pass

    def test_get_dynamicIp(self):
        rv = self.app.get('/dynamicIp')
        assert 'ip' in rv.data

    def test_set_dynamicIp(self):
        rv = self.app.get('/dynamicIp?setip=192.168.1.1')
        assert '{"ip":"192.168.1.1"}' in rv.data

    def test_post_dynamicIp(self):
        rv = self.app.post('/dynamicIp', data=None,
                           follow_redirects=True)
        assert 'Post return None' in rv.data


if __name__ == '__main__':
    unittest.main()

