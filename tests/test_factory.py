from flaskr import create_app


def test_config():
    # creates a new app with specific config
    assert not create_app().testing # assert that there is no testing config
    assert create_app({'TESTING': True}).testing # assert that there is a testing config


def test_hello(client):
    # uses the client to make a GET request to the /hello endpoint
    response = client.get('/hello')
    assert response.data == b'Hello, World!' # assert that the response data matches the expected output
