def app(env, start_response):
    print("IN APP")
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Hello World']