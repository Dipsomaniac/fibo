def test_tests():
    """Just ensure that the tests are working."""
    assert True


def test_fibo(benchmark):
    from fibo import fibo

    benchmark(fibo, 0, 1, 1000)

    assert fibo(5, 8, 5) == (55, 89, [5, 8, 13, 21, 34])
    assert fibo(55, 89, 5) == (610, 987, [55, 89, 144, 233, 377])


def test_rest(client, loop):
    response = client.get('/', status=400)
    assert 'Bad number' in response.text

    response = client.get('/-50', status=400)
    assert 'Bad number' in response.text

    response = client.get('/0')
    assert response.status_code == 200
