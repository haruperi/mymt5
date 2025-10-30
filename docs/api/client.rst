MT5Client
=========

.. automodule:: mymt5.client
   :members:
   :undoc-members:
   :show-inheritance:

MT5Client Class
---------------

.. autoclass:: mymt5.client.MT5Client
   :members:
   :undoc-members:
   :special-members: __init__
   :show-inheritance:

Connection Methods
------------------

.. automethod:: mymt5.client.MT5Client.initialize
.. automethod:: mymt5.client.MT5Client.connect
.. automethod:: mymt5.client.MT5Client.disconnect
.. automethod:: mymt5.client.MT5Client.shutdown
.. automethod:: mymt5.client.MT5Client.is_connected
.. automethod:: mymt5.client.MT5Client.reconnect

Authentication
--------------

.. automethod:: mymt5.client.MT5Client.login
.. automethod:: mymt5.client.MT5Client.logout

Auto-Reconnection
-----------------

.. automethod:: mymt5.client.MT5Client.enable_auto_reconnect
.. automethod:: mymt5.client.MT5Client.disable_auto_reconnect
.. automethod:: mymt5.client.MT5Client.set_retry_attempts
.. automethod:: mymt5.client.MT5Client.set_retry_delay

Multi-Account
-------------

.. automethod:: mymt5.client.MT5Client.switch_account
.. automethod:: mymt5.client.MT5Client.save_account
.. automethod:: mymt5.client.MT5Client.load_account
.. automethod:: mymt5.client.MT5Client.list_accounts
.. automethod:: mymt5.client.MT5Client.remove_account

Events
------

.. automethod:: mymt5.client.MT5Client.on
.. automethod:: mymt5.client.MT5Client.off
.. automethod:: mymt5.client.MT5Client.trigger_event

Status & Diagnostics
--------------------

.. automethod:: mymt5.client.MT5Client.get_status
.. automethod:: mymt5.client.MT5Client.get_connection_statistics
.. automethod:: mymt5.client.MT5Client.get_error
.. automethod:: mymt5.client.MT5Client.ping

