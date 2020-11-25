.. image:: https://travis-ci.org/ambitioninc/rabbitmq-admin.svg?branch=master
    :target: https://travis-ci.org/ambitioninc/rabbitmq-admin

.. image:: https://coveralls.io/repos/ambitioninc/rabbitmq-admin/badge.png?branch=master
    :target: https://coveralls.io/r/ambitioninc/rabbitmq-admin?branch=master


rabbitmq-api-admin
==================
This project was taken from fork https://github.com/vaseemShaikh/rabbitmq-admin
(last commit 996b3d386d17564faf317b1cd6bce4cf20348a74)


Example
-------
::

    >>> from rabbitmq_admin import AdminAPI
    >>> api = AdminAPI(url='http://192.168.99.100:15672', auth=('guest', 'guest'))
    >>> api.create_vhost('second_vhost')
    >>> api.create_user('second_user', 'password')
    >>> api.create_user_permission('second_user', 'second_vhost')
    >>> api.list_permission()
    [{'configure': '.*',
      'read': '.*',
      'user': 'guest',
      'vhost': '/',
      'write': '.*'},
     {'configure': '.*',
      'read': '.*',
      'user': 'second_user',
      'vhost': 'second_vhost',
      'write': '.*'}]

Unsupported Management API endpoints
------------------------------------
This is a list of unsupported API endpoints:

- ``/api/exchanges/vhost/name/bindings/source [GET]``
- ``/api/exchanges/vhost/name/bindings/destination [GET]``
- ``/api/exchanges/vhost/name/publish [POST]``
- ``/api/queues/vhost/name/contents [DELETE]``
- ``/api/queues/vhost/name/actions [POST]``
- ``/api/bindings/vhost/e/exchange/q/queue [GET, POST]``
- ``/api/bindings/vhost/e/exchange/q/queue/props [GET, DELETE]``
- ``/api/bindings/vhost/e/source/e/destination [GET, POST]``
- ``/api/bindings/vhost/e/source/e/destination/props [GET, DELETE]``
- ``/api/parameters [GET]``
- ``/api/parameters/component [GET]``
- ``/api/parameters/component/vhost [GET]``
- ``/api/parameters/component/vhost/name [GET, PUT, DELETE]``


Documentation
-------------
Documentation is available at http://rabbitmq-admin.readthedocs.org

License
-------
Apache License 2.0 (see LICENSE)
