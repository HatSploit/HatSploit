#!/usr/bin/env python3

#
# MIT License
#
# Copyright (c) 2020-2021 EntySec
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from flask import Flask, json
from flask_restful import Resource, Api, reqparse
import ast
import logging

from hatsploit.lib.sessions import Sessions

class SessionManager(Resource):
    sessions = Sessions()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('platform', required=False)
        parser.add_argument('type', required=False)
        parser.add_argument('id', required=False)
        parser.add_argument('command', required=False)
        parser.add_argument('close', required=False)
        parser.add_argument('count', required=False)
        args = parser.parse_args()

        if args['platform'] and args['type'] and args['id'] and args['command']:
            session = self.sessions.get_session(
                args['platform'], args['type'], args['id']
            )

            if session:
                return session.send_command(args['command'], output=True), 200
            return "", 200

        elif args['platform'] and args['id'] and args['close']:
            self.sessions.close_session(
                args['platform'], args['id']
            )

            return "", 200

        elif args['count']:
            sessions = self.sessions.get_all_sessions()
            if sessions:
                if args['platform']:
                    if platform in sessions.keys():
                        return len(sessions[platform]), 200
                    return 0, 200
                return len(sessions), 200
            return 0, 200

        sessions = self.sessions.get_all_sessions()
        if sessions:
            data = dict()
            for platform in sessions.keys():
                for session_id in sessions[platform].keys():
                    data[platform][session_id]['type'] = sessions[platform][session_id]['type']
                    data[platform][session_id]['host'] = sessions[platform][session_id]['host']
                    data[platform][session_id]['port'] = sessions[platform][session_id]['port']
            return data, 200
        return dict(), 200

class API:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)

    def init(self):
        self.api.add_resource(SessionManager, '/sessions')
        #self.app.logger.disabled = True
        #log = logging.getLogger('werkzeug')
        #log.disabled = True
        self.app.run()
    
