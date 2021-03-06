import os
import time
from unittest import TestCase

import pika
import requests
from requests import HTTPError

from rabbitmq_admin.api import RabbitAPIClient


class RabbitAPIClientTests(TestCase):
    """
    These test cases require a docker container up and running.
    See CONTRIBUTING.md
    """

    @classmethod
    def setUpClass(cls):
        """
        One-time set up that connects as 'guest', creates a 'test_queue' and
        sends one message.
        """
        cls.host = os.environ.get('RABBITMQ_HOST', '127.0.0.1')
        cls.amqp_port = 5672
        cls.admin_port = 15672

        credentials = pika.PlainCredentials('guest', 'guest')
        cls.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                cls.host,
                port=cls.amqp_port,
                credentials=credentials
            ),
        )
        cls.channel = cls.connection.channel()
        cls.queue_name = 'test_queue'
        cls.channel.queue_declare(queue=cls.queue_name)
        cls.channel.basic_publish(
            exchange='',
            routing_key=cls.queue_name,
            body='Test Message')

        cls.api = RabbitAPIClient(cls.host, cls.admin_port,
                                  auth=('guest', 'guest'))

        # connection statistics appear with a delay therefore:
        time.sleep(5)

        cls.node_name = cls.api.list_nodes()[0]['name']

    @classmethod
    def tearDownClass(cls):
        cls.channel.queue_delete(cls.queue_name)
        cls.connection.close()

    def test_overview(self):
        response = self.api.overview()
        self.assertIsInstance(response, dict)

    def test_get_cluster_name(self):
        self.assertTrue(
            self.api.get_cluster_name()['name'].startswith('rabbit@')
        )

    def test_list_nodes(self):
        self.assertEqual(
            len(self.api.list_nodes()),
            1
        )

    def test_get_node(self):
        response = self.api.get_node(self.node_name)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['name'], self.node_name)

    def test_list_extensions(self):
        self.assertEqual(
            self.api.list_extensions(),
            [{'javascript': 'dispatcher.js'}]
        )

    def test_get_definitions(self):
        response = self.api.get_definitions()
        self.assertEqual(len(response['users']), 1)
        self.assertEqual(len(response['vhosts']), 1)

    def test_post_definitions(self):
        response = self.api.get_definitions()
        self.api.post_definitions(response)

    def test_list_connections(self):
        self.assertEqual(
            len(self.api.list_connections()),
            1
        )

    def test_get_connection(self):
        cname = self.api.list_connections()[0].get('name')
        self.assertIsInstance(
            self.api.get_connection(cname),
            dict
        )

    def test_delete_connection(self):
        with self.assertRaises(requests.HTTPError):
            self.api.delete_connection('not-a-connection')

    def test_delete_connection_with_reson(self):
        with self.assertRaises(requests.HTTPError):
            self.api.delete_connection('not-a-connection', 'I don\'t like you')

    def test_list_connection_channels(self):
        cname = self.api.list_connections()[0].get('name')
        response = self.api.list_connection_channels(cname)

        self.assertEqual(
            response[0].get('name'),
            cname + ' (1)'
        )

    def test_list_channels(self):
        self.assertEqual(
            len(self.api.list_channels()),
            1
        )

    def test_get_channel(self):
        cname = self.api.list_channels()[0].get('name')
        self.assertIsInstance(
            self.api.get_channel(cname),
            dict
        )

    def test_list_consumers(self):
        self.assertEqual(
            self.api.list_consumers(),
            []
        )

    def test_list_consumers_for_vhost(self):
        self.assertEqual(
            self.api.list_consumers_for_vhost('/'),
            []
        )

    def test_list_exchanges(self):
        self.assertEqual(
            len(self.api.list_exchanges()),
            7
        )

    def test_list_exchanges_for_vhost(self):
        self.assertEqual(
            len(self.api.list_exchanges_for_vhost('/')),
            7
        )

    def test_get_create_delete_exchange_for_vhost(self):
        name = 'myexchange'
        body = {
            "type": "direct",
            "auto_delete": False,
            "durable": False,
            "internal": False,
            "arguments": {}
        }
        self.api.create_exchange_for_vhost(name, '/', body)
        self.assertEqual(
            len(self.api.list_exchanges_for_vhost('/')),
            8
        )
        self.assertEqual(
            self.api.get_exchange_for_vhost(name, '/').get('name'),
            name
        )

        self.api.delete_exchange_for_vhost(name, '/')
        self.assertEqual(
            len(self.api.list_exchanges_for_vhost('/')),
            7
        )

    def test_list_bindings(self):
        self.assertIn(
            {
                'arguments': {},
                'destination': 'test_queue',
                'destination_type': 'queue',
                'properties_key': 'test_queue',
                'routing_key': 'test_queue',
                'source': '',
                'vhost': '/'
            },
            self.api.list_bindings()
        )

    def test_list_bindings_for_vhost(self):
        self.assertIn(
            {
                'arguments': {},
                'destination': 'test_queue',
                'destination_type': 'queue',
                'properties_key': 'test_queue',
                'routing_key': 'test_queue',
                'source': '',
                'vhost': '/'
            },
            self.api.list_bindings_for_vhost('/')
        )

    def test_list_bindings_by_queue(self):
        self.assertIn(
            {
                'arguments': {},
                'destination': 'test_queue',
                'destination_type': 'queue',
                'properties_key': 'test_queue',
                'routing_key': 'test_queue',
                'source': '',
                'vhost': '/'
            },
            self.api.list_bindings_by_queue(self.queue_name, '/')
        )

    def test_get_messages(self):
        message = self.api.extract_messages(self.queue_name, '/')[0]
        self.assertEqual(message['payload'], 'Test Message')

    def test_list_vhosts(self):
        response = self.api.list_vhosts()
        self.assertEqual(
            len(response),
            1
        )
        self.assertEqual(response[0].get('name'), '/')

    def test_get_vhosts(self):
        response = self.api.get_vhost('/')
        self.assertEqual(response.get('name'), '/')

    def test_create_delete_vhost(self):
        name = '/vhost-2'

        self.api.create_vhost(name)
        self.assertEqual(
            len(self.api.list_vhosts()),
            2
        )

        self.api.delete_vhost(name)
        self.assertEqual(
            len(self.api.list_vhosts()),
            1
        )

    def test_create_delete_vhost_tracing(self):
        name = 'vhost2'

        self.api.create_vhost(name, tracing=True)
        self.assertEqual(
            len(self.api.list_vhosts()),
            2
        )

        self.api.delete_vhost(name)
        self.assertEqual(
            len(self.api.list_vhosts()),
            1
        )

    def test_list_users(self):
        self.assertEqual(
            len(self.api.list_users()),
            1
        )

    def test_get_user(self):
        response = self.api.get_user('guest')
        self.assertEqual(response.get('name'), 'guest')
        self.assertEqual(response.get('tags'), 'administrator')

    def test_create_delete_user(self):
        name = 'user2'
        password_hash = '5f4dcc3b5aa765d61d8327deb882cf99'  # md5 of 'password'

        self.api.create_user(name, password='', password_hash=password_hash)
        self.assertEqual(
            len(self.api.list_users()),
            2
        )

        self.api.delete_user(name)
        self.assertEqual(
            len(self.api.list_users()),
            1
        )

    def test_create_delete_user_password(self):
        name = 'user2'
        password = 'password'

        self.api.create_user(name, password=password)
        self.assertEqual(
            len(self.api.list_users()),
            2
        )

        self.api.delete_user(name)
        self.assertEqual(
            len(self.api.list_users()),
            1
        )

    def test_create_delete_user_no_password(self):
        name = 'user2'
        password = ''

        self.api.create_user(name, password=password)
        self.assertEqual(
            len(self.api.list_users()),
            2
        )

        self.api.delete_user(name)
        self.assertEqual(
            len(self.api.list_users()),
            1
        )

    def test_list_user_permissions(self):
        self.assertEqual(
            self.api.list_user_permissions('guest'),
            [{'configure': '.*',
              'read': '.*',
              'user': 'guest',
              'vhost': '/',
              'write': '.*'}]
        )

    def test_whoami(self):
        self.assertEqual(
            self.api.whoami(),
            {'name': 'guest', 'tags': 'administrator'}
        )

    def test_list_permissions(self):
        self.assertEqual(
            self.api.list_permissions(),
            [{'configure': '.*',
              'read': '.*',
              'user': 'guest',
              'vhost': '/',
              'write': '.*'}]
        )

    def test_get_user_permission(self):
        self.assertEqual(
            self.api.get_user_permission('/', 'guest'),
            {
                'configure': '.*',
                'read': '.*',
                'user': 'guest',
                'vhost': '/',
                'write': '.*'
            }
        )

    def test_create_delete_user_permission(self):
        uname = 'test_user'
        vname = 'test_vhost'
        password_hash = '5f4dcc3b5aa765d61d8327deb882cf99'  # md5 of 'password'

        # Create test user/vhost
        self.api.create_user(uname, password='', password_hash=password_hash)
        self.api.create_vhost(vname)

        self.assertEqual(len(self.api.list_user_permissions(uname)), 0)

        # Create the permission
        self.api.create_user_permission(uname, vname)

        self.assertEqual(len(self.api.list_user_permissions(uname)), 1)

        # Delete the permission
        self.api.delete_user_permission(uname, vname)

        self.assertEqual(len(self.api.list_user_permissions(uname)), 0)
        # delete test user/vhost
        self.api.delete_user(uname)
        self.api.delete_vhost(vname)

    def test_policies(self):
        # Create a policy
        self.api.create_policy_for_vhost(
            vhost="/",
            name="ha-all",
            definition={"ha-mode": "all"},
            pattern="",
            apply_to="all",
        )

        list_all_response = self.api.list_policies()
        list_default_response = self.api.list_policies_for_vhost("/")

        self.assertEqual(list_all_response, list_default_response)
        self.assertEqual(len(list_default_response), 1)

        with self.assertRaises(HTTPError):
            self.api.get_policy_for_vhost("/", "not-a-policy")

        get_response = self.api.get_policy_for_vhost("/", "ha-all")
        self.assertEqual(
            get_response,
            list_all_response[0]
        )

        self.api.delete_policy_for_vhost("/", "ha-all")
        self.assertEqual(
            len(self.api.list_policies()),
            0
        )

    def test_is_vhost_alive(self):
        self.assertDictEqual(
            self.api.is_vhost_alive('/'),
            {'status': 'ok'}
        )
        self.channel.queue_delete('aliveness-test')

    def test_list_queues(self):
        self.assertEqual(
            len(self.api.list_queues()),
            1
        )

    def test_list_queues_for_vhost(self):
        self.assertEqual(
            len(self.api.list_queues_for_vhost('/')),
            1
        )

    def test_get_create_delete_queue_for_vhost(self):
        name = 'my_queue'
        body = {
            "auto_delete": False,
            "durable": True,
            "arguments": {},
            "node": self.node_name
        }
        self.api.create_queue_for_vhost(name, '/', body)
        self.assertEqual(
            len(self.api.list_queues_for_vhost('/')),
            2
        )
        self.assertEqual(
            self.api.get_queue_for_vhost(name, '/').get('name'),
            name
        )

        self.api.delete_queue_for_vhost(name, '/')
        self.assertEqual(
            len(self.api.list_queues_for_vhost('/')),
            1
        )

        with self.assertRaises(HTTPError):
            self.api.get_queue_for_vhost(name, '/')
