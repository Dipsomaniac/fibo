import asyncio
import logging

import muffin


__version__ = "0.0.6"
__project__ = "fibo"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


# Initialize the application
app = muffin.Application('fibo', CONFIG='fibo.config', VERSION=__version__)

logging.info('Start application %s, chunk size: %s', __version__, app.cfg.CHUNK_SIZE)


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
    size, size_min, size_step = app.cfg.CHUNK_SIZE, app.cfg.CHUNK_SIZE_MIN, app.cfg.CHUNK_SIZE_STEP
    wait_time = app.cfg.CHUNK_WAIT_TIME

    # If num is small we use precalculated results
    if num <= size:
        yield from response.write(', '.join(map(str, FIBO[:num])).encode())

    else:
        # First chunk is already calculated
        yield from response.write(', '.join(map(str, FIBO)).encode())
        a, b, num = A, B, num - size
        while num:
            yield from response.write(b', ')
            todo = size if size <= num else num
            num -= todo
            time = app.loop.time()
            a, b, result = yield from asyncio.ensure_future(fibo_coro(a, b, todo), loop=app.loop)
            yield from response.write(', '.join(map(str, result)).encode())
            diff = app.loop.time() - time
            if diff > wait_time:
                size = max(size-size_step, size_min)

    yield from response.write(b']')
    yield from response.write_eof()
