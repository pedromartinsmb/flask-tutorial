# The only behaviour that can change in the factory code is passing test
# config. If the config is not passed, there should be some default
# configuration, otherwise the configuration should be overridden.

from flaskr import create_app

def test_config():
    
    # "assert" tests a condition and returns AssertionError if it's not True
    
    # The "testing" attribute of and app returns True if "'TESTING': True" was
    # informed in the app config dict
    assert not create_app().testing

    # Checks if an app created with "'TESTING': True" is indeed configured as
    # a testing app
    assert create_app({'TESTING': True}).testing

# As this function expects and argument named "client", Pytest will search for
# a fixture function named "client", run it and pass its return value to the
# "test_hello" function below
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
