import os

config = {
    'debug': True,
    'autoreload': True,
    'web_port': 8086,
    'tornado': {
        'web_path': os.path.abspath(os.path.join(os.path.dirname(__file__), 'web')),
        'html_path': os.path.abspath(os.path.join(os.path.dirname(__file__), 'web/html')),
        'static_path': os.path.abspath(os.path.join(os.path.dirname(__file__), 'web/static')),
        'upload_path': os.path.abspath(os.path.join(os.path.dirname(__file__), 'upload')),
        'tmp_path': os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp')),
        # unused for now:
        'cookie_secret': '__TODO:_GENERATE_YOURx_OWN_RANDOM_VALUE_HERE__',
        'login_url': '/login',
        # Disable login for now:
        'xsrf_cookies': False,
    }
}
