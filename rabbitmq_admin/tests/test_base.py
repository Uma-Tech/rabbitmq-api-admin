from unittest import TestCase

from unittest.mock import patch, Mock
import requests

from rabbitmq_admin.base import Resource


class ResourceTests(TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:15672'
        self.host = '127.0.0.1'
        self.port = 15672
        self.auth = ('guest', 'guest')

        self.resource = Resource(self.host, self.port, self.auth)

    def test_init(self):
        self.assertEqual(self.resource.url, self.url)
        self.assertEqual(self.resource.auth, self.auth)
        self.assertEqual(self.resource.headers,
                         {'Content-type': 'application/json'})

    @patch.object(requests, 'put', autospec=True)
    def test_put_no_data(self, mock_put):

        mock_response = Mock()
        mock_put.return_value = mock_response

        self.resource._put(self.url, auth=self.auth)

        mock_response.raise_for_status.assert_called_once_with()

    @patch.object(Resource, '_post')
    def test_api_post(self, mock_post):
        url = '/api/definitions'
        headers = {'k1': 'v1'}

        self.resource._api_post(url, headers=headers)
        mock_post.assert_called_once_with(
            url=self.url + url,
            auth=self.auth,
            headers={
                'k1': 'v1',
                'Content-type': 'application/json'
            },
            timeout=10
        )

    @patch.object(requests, 'post', autospec=True)
    def test_post_no_data(self, mock_post):

        mock_response = Mock()
        mock_post.return_value = mock_response

        self.resource._post(self.url, auth=self.auth)

        mock_response.raise_for_status.assert_called_once_with()

    @patch.object(requests, 'post', autospec=True)
    def test_post(self, mock_post):

        mock_response = Mock()
        mock_post.return_value = mock_response

        self.resource._post(self.url, auth=self.auth, data={'hello': 'world'})

        mock_response.raise_for_status.assert_called_once_with()
