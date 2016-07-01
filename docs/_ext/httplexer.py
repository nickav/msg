def setup(app):
    # enable Pygments http lexer
    try:
        import pygments
        if pygments.__version__ >= '1.5':
            # use HTTP lexer included in recent versions of Pygments
            from pygments.lexers import HttpLexer
        else:
            # use HTTP lexer from pygments-json if installed
            from pygson.http_lexer import HTTPLexer as HttpLexer
    except ImportError:
        pass  # not fatal if we have old (or no) Pygments and no pygments-http
    else:
        app.add_lexer('http', HttpLexer())