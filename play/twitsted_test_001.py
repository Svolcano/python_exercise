def hello():
    print("hello from reactor loop")
    print("lately i feel like i'm stuck in a rut.")

from twisted.internet import reactor

reactor.callWhenRunning(hello)
print("Starting the reactor.")
reactor.run()