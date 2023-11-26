#!/usr/bin/env python3

import tornado
import tornado.web
import tornado.ioloop

import asyncio
import logging
import signal

from overview_handler import OverviewHandler
from control_handler import ControlHandler

from endpoints import endpoints
from config import config

def shutdown_server():
    logging.info('server shutting down')
    tornado.ioloop.IOLoop.instance().stop()

def signal_exit(signum, frame):
    # add callback to close on next ioloop iteration
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(shutdown_server)

def setup():
    app = tornado.web.Application(
        [(endpoints['landing'], OverviewHandler,
          {'html_path': config['tornado']['html_path']}
          ),
         (endpoints['control'], ControlHandler,
          {'html_path': config['tornado']['html_path']}
          ),
         (r'/static/(.*)', tornado.web.StaticFileHandler,
          {'path': config['tornado']['static_path']}
          )],
        **config['tornado'], debug=config['debug'], autoreload=config['autoreload'])

    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    return app

async def main():
    app = setup()
    app.listen(config['web_port'])
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()

if __name__ == '__main__':
    asyncio.run(main())
