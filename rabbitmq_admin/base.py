import json
import requests
from copy import deepcopy


class Resource(object):
    """
    A base class for API resources
    """

    # """List of allowed methods, allowed values are
    # ```['GET', 'PUT', 'POST', 'DELETE']``"""
    # ALLOWED_METHODS = []

    def __init__(self, host, port, auth, scheme='http', timeout=10):
        """
        :param host: The RabbitMQ API host to connect to
        :type host: str

        :param port: port of RabbitMQ API
        :type port: int

        :param scheme: the protocol name
        :type scheme: str

        :param auth: The authentication to pass to the request. See
            `Requests' authentication`_ documentation. For the simplest case of
            a username and password, simply pass in a tuple of
            ``('username', 'password')``
        :type auth: Requests auth

        .. _Requests' authentication:
        http://docs.python-requests.org/en/latest/user/authentication/
        """
        self.url = f'{scheme}://{host}:{port}'
        self.auth = auth
        self.timeout = timeout

        self.headers = {
            'Content-type': 'application/json',
        }

    def _api_get(self, url, **kwargs):
        """
        A convenience wrapper for _get. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['timeout'] = self.timeout
        return self._get(**kwargs)

    def _get(self, *args, **kwargs):
        """
        A wrapper for getting things

        :returns: The response of your get
        :rtype: dict
        """
        response = requests.get(*args, **kwargs)

        response.raise_for_status()

        return response.json()

    def _api_put(self, url, **kwargs):
        """
        A convenience wrapper for _put. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['timeout'] = self.timeout
        self._put(**kwargs)

    def _put(self, *args, **kwargs):
        """
        A wrapper for putting things. It will also json encode your 'data'
        parameter

        :returns: The response of your put
        :rtype: dict
        """
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.put(*args, **kwargs)
        response.raise_for_status()

    def _api_post(self, url, **kwargs):
        """
        A convenience wrapper for _post. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['timeout'] = self.timeout
        return self._post(**kwargs)

    def _post(self, *args, **kwargs):
        """
        A wrapper for posting things. It will also json encode your 'data'
        parameter

        :returns: The response of your post
        :rtype: dict
        """
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.post(*args, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def _api_delete(self, url, **kwargs):
        """
        A convenience wrapper for _delete. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['timeout'] = self.timeout
        self._delete(**kwargs)

    def _delete(self, *args, **kwargs):
        """
        A wrapper for deleting things

        :returns: The response of your delete
        :rtype: dict
        """
        response = requests.delete(*args, **kwargs)
        response.raise_for_status()
