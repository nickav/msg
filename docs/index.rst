Messaging API
=========================================
Welcome to the Messaging API, a RESTful API for sending and receiving messages. All endpoints return JSON responses.

Users
----------------------------------------

    The Users object represents a user that can send and receive messages. The user object looks like this:

    .. sourcecode:: json

        {
            "created_time": "Tue, 25 Aug 2015 18:30:27 GMT",
            "id": 2,
            "name": "ben",
            "full_name": "Ben Bederson",
            "received_messages": [],
            "sent_messages": []
        }

    Where received_messages and sent_messages are arrays of sent and recieved `Messages <#id5>`_.

    The following actions can be performed on messages:

.. autoflask:: app.routes:app
    :undoc-static:
    :undoc-endpoints: messages, messages_create, message, messages_bulk

Messages
----------------------------------------

    The Message object represents a single message sent from one user to another. The message object looks like this:

    .. sourcecode:: json

        {
            "content": "hey!",
            "delivered_time": null,
            "from_id": 1,
            "id": 1,
            "read_time": null,
            "sent_time": "Tue, 25 Aug 2015 18:30:27 GMT",
            "to_id": 2
        }

    Where from_id and to_id are the corresponding `Users <#users>`_. The following actions can be performed on messages:

.. autoflask:: app.routes:app
    :undoc-static:
    :endpoints: messages, messages_create, message, messages_bulk

