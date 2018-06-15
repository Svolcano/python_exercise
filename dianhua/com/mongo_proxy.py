import time
import pymongo
from pymongo.errors import AutoReconnect, ProtocolError

def get_methods(*objs):
    return set(
        attr
        for obj in objs
        for attr in dir(obj)
        if not attr.startswith('_') and hasattr(getattr(obj, attr), '__call__')
    )

try:
    # will fail to import from older versions of pymongo
    from pymongo import MongoClient, MongoReplicaSetClient
except ImportError:
    MongoClient, MongoReplicaSetClient = None, None

try:
    from pymongo import Connection, ReplicaSetConnection
except ImportError:
    Connection, ReplicaSetConnection = None, None

EXECUTABLE_MONGO_METHODS = get_methods(pymongo.collection.Collection,
                                       pymongo.database.Database,
                                       Connection,
                                       ReplicaSetConnection,
                                       MongoClient, MongoReplicaSetClient,
                                       pymongo)


def get_connection(obj):
    if isinstance(obj, pymongo.collection.Collection):
        return obj.database.client
    elif isinstance(obj, pymongo.database.Database):
        return obj.client
    elif isinstance(obj, (MongoClient, MongoReplicaSetClient)):
        return obj
    else:
        return None


class Executable(object):
    """ Wrap a MongoDB-method and handle AutoReconnect-exceptions
    using the safe_mongocall decorator.
    """

    def __init__(self, method, wait_time=None,
                 disconnect_on_timeout=True):
        self.method = method
        # MongoDB's documentation claims that replicaset elections
        # shouldn't take more than a minute. In our experience, we've
        # seen them take as long as a minute and a half, so regardless
        # of what the documentation says, we're going to give the
        # connection two minutes to recover.
        self.wait_time = wait_time or 30
        self.disconnect_on_timeout = disconnect_on_timeout

    def __call__(self, *args, **kwargs):
        """ Automatic handling of AutoReconnect-exceptions.
        """
        start = time.time()
        i = 0
        disconnected = False
        max_time = self.wait_time
        while True:
            try:
                # test ping
                self.method.__self__.database.command('ping')
                return self.method(*args, **kwargs)
            except AutoReconnect, ProtocolError:
                end = time.time()
                delta = end - start
                print delta
                if delta >= max_time:
                    if not self.disconnect_on_timeout or disconnected:
                        break
                    conn = get_connection(self.method.__self__)
                    if conn:
                        conn.close()
                        disconnected = True
                        max_time *= 2
                        i = 0
                time.sleep(min(5, pow(2, i)))
                i += 1
        # Try one more time, but this time, if it fails, let the
        # exception bubble up to the caller.
        return self.method(*args, **kwargs)

    def __dir__(self):
        return dir(self.method)

    def __str__(self):
        return self.method.__str__()

    def __repr__(self):
        return self.method.__repr__()


class MongoProxy(object):
    """ Proxy for MongoDB connection.
    Methods that are executable, i.e find, insert etc, get wrapped in an
    Executable-instance that handles AutoReconnect-exceptions transparently.
    """
    def __init__(self, conn, wait_time=None,
                 disconnect_on_timeout=True):
        """ conn is an ordinary MongoDB-connection.
        """
        self.conn = conn
        self.wait_time = wait_time
        self.disconnect_on_timeout = disconnect_on_timeout

    def __getitem__(self, key):
        """ Create and return proxy around the method in the connection
        named "key".
        """
        item = self.conn[key]
        if hasattr(item, '__call__'):
            return MongoProxy(item, self.wait_time)
        return item

    def __getattr__(self, key):
        """ If key is the name of an executable method in the MongoDB connection,
        for instance find or insert, wrap this method in Executable-class that
        handles AutoReconnect-Exception.
        """

        attr = getattr(self.conn, key)
        if hasattr(attr, '__call__'):
            if key in EXECUTABLE_MONGO_METHODS:
                return Executable(attr, self.wait_time)
            else:
                return MongoProxy(attr, self.wait_time)
        return attr

    def __call__(self, *args, **kwargs):
        return self.conn(*args, **kwargs)

    def __dir__(self):
        return dir(self.conn)

    def __str__(self):
        return self.conn.__str__()

    def __repr__(self):
        return self.conn.__repr__()

    def __nonzero__(self):
        return True