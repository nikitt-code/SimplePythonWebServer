import Server

app = Server.LIDServer('0.0.0.0', 8000)


@app.setRoute('/test1')
def test_1():
    status = "ok"  # ok/error
    code = "200"  # 200/404/500/301...
    contents = "<b>Hello, World!</b>"  # Any text or something else

    # You can use this: Server.response_ok('test')
    # You can use this: Server.response_error(404, 'PageNotFound')
    # You can use this: Server.response_json({'test': 1})
    # You can use this: ("ok", 200, "contents")

    return (status, code, contents)


app.start()
