import asyncio

import muffin


__version__ = "0.0.3"
__project__ = "fibo"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


# Initialize the application
app = muffin.Application('fibo', CONFIG='fibo.config', VERSION=__version__)


# Send current version in headers
@asyncio.coroutine
def on_prepare(request, response):
    """Put the application version to headers."""
    response.headers['X-App-Version'] = __version__

app.on_response_prepare.append(on_prepare)


try:
    from fibo.fibonacci import fibo
except ImportError:
    def fibo(a, b, todo=app.cfg.CHUNK_SIZE):
        result = []
        for _ in range(todo):
            result.append(a)
            a, b = b, a + b
        return a, b, result


# Precalculate results for first chunk (by default is first 1000)
A, B, FIBO = fibo(0, 1, todo=app.cfg.CHUNK_SIZE)

fibo_coro = asyncio.coroutine(fibo)


@app.register('/', '/{num:-?\d+}')
def magic(request):
    try:
        num = int(request.match_info['num'])
        assert num >= 0
    except (ValueError, KeyError, AssertionError):
        raise muffin.HTTPBadRequest(reason='Bad number')

    response = muffin.StreamResponse(headers={'Content-Type': 'application/json'}).start(request)

    # If num is small we use precalculated results
    if num <= app.cfg.CHUNK_SIZE:
        yield from response.write(', '.join(map(str, FIBO[:num])).encode())

    else:
        # First chunk is already calculated
        yield from response.write(', '.join(map(str, FIBO)).encode())
        a, b, num = A, B, num - app.cfg.CHUNK_SIZE
        while num:
            yield from response.write(b', ')
            todo = app.cfg.CHUNK_SIZE if app.cfg.CHUNK_SIZE <= num else num
            num -= todo
            a, b, result = yield from asyncio.ensure_future(fibo_coro(a, b, todo))
            yield from response.write(', '.join(map(str, result)).encode())

    yield from response.write(b']')
    yield from response.write_eof()
