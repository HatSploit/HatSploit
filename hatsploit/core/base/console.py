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

import os
import readline
import sys

from hatsploit.core.base.exceptions import Exceptions
from hatsploit.core.base.execute import Execute
from hatsploit.core.base.loader import Loader

from hatsploit.core.cli.fmt import FMT
from hatsploit.core.cli.badges import Badges

from hatsploit.core.utils.ui.banner import Banner
from hatsploit.core.utils.ui.tip import Tip

from hatsploit.lib.config import Config
from hatsploit.lib.jobs import Jobs
from hatsploit.lib.sessions import Sessions
from hatsploit.lib.modules import Modules
from hatsploit.lib.payloads import Payloads
from hatsploit.lib.storage import LocalStorage


class Console:
    exceptions = Exceptions()
    execute = Execute()
    loader = Loader()

    fmt = FMT()
    badges = Badges()

    banner = Banner()
    tip = Tip()

    config = Config()
    jobs = Jobs()
    sessions = Sessions()
    modules = Modules()
    payloads = Payloads()
    local_storage = LocalStorage()

    history = config.path_config['history_path']
    prompt = config.core_config['details']['prompt']

    handler_options = {}

    def check_install(self):
        if os.path.exists(self.config.path_config['root_path']):
            workspace = self.config.path_config['user_path']

            if not os.path.exists(workspace):
                self.badges.print_process(f"Creating workspace at {workspace}...")
                os.mkdir(workspace)

            return True
        self.badges.print_error("HatSploit is not installed!")
        self.badges.print_information("Consider running installation.")
        return False

    def start_hsf(self):
        try:
            self.loader.load_all()
        except Exception:
            sys.exit(1)

    def update_events(self):
        self.jobs.stop_dead()
        self.sessions.close_dead()
        self.add_handler_options()

    def launch_menu(self):
        while True:
            try:
                if not self.modules.check_current_module():
                    prompt = f'({self.prompt})> '
                else:
                    module = self.modules.get_current_module_name()
                    name = self.modules.get_current_module_object().details['Name']

                    prompt = f'({self.prompt}: {module.split("/")[0]}: %red{name}%end)> '
                commands = self.badges.input_empty(prompt)

                self.update_events()
                self.execute.execute_command(commands)
                self.update_events()

                if self.local_storage.get("history"):
                    readline.write_history_file(self.history)

            except (KeyboardInterrupt, EOFError, self.exceptions.GlobalException):
                pass
            except Exception as e:
                self.badges.print_error("An error occurred: " + str(e) + "!")

    def enable_history_file(self):
        if not os.path.exists(self.history):
            open(self.history, 'w').close()
        readline.read_history_file(self.history)

    def launch_history(self):
        readline.set_auto_history(False)

        using_history = self.local_storage.get("history")
        if using_history:
            readline.set_auto_history(True)
            self.enable_history_file()

        readline.parse_and_bind("tab: complete")

    def launch_shell(self):
        version = self.config.core_config['details']['version']
        codename = self.config.core_config['details']['codename']

        if self.config.core_config['console']['clear']:
            self.badges.print_empty("%clear", end='')

        if self.config.core_config['console']['banner']:
            self.banner.print_random_banner()

        if self.config.core_config['console']['header']:
            plugins = self.local_storage.get("plugins")
            modules = self.local_storage.get("modules")
            payloads = self.local_storage.get("payloads")

            plugins_total = 0
            modules_total = 0
            payloads_total = 0

            if payloads:
                for database in payloads:
                    payloads_total += len(payloads[database])
            if plugins:
                for database in plugins:
                    plugins_total += len(plugins[database])
            if modules:
                for database in modules:
                    modules_total += len(modules[database])

            header = ""
            header += "%end\n"
            if codename:
                header += f"    --=( %yellowHatSploit Framework {version} {codename}%end\n"
            else:
                header += f"    --=( %yellowHatSploit Framework {version}%end\n"
            header += "--==--=( Developed by EntySec (%linehttps://entysec.netlify.app/%end)\n"
            header += f"    --=( {modules_total} modules | {payloads_total} payloads | {plugins_total} plugins\n"
            header += "%end"

            self.badges.print_empty(header)

        if self.config.core_config['console']['tip']:
            self.tip.print_random_tip()
            self.badges.print_empty()

    def shell(self):
        self.start_hsf()
        self.launch_history()
        self.launch_shell()
        self.launch_menu()

    def script(self, input_files, do_shell=False):
        self.start_hsf()
        self.launch_shell()

        for input_file in input_files:
            if os.path.exists(input_file):
                file = open(input_file, 'r')
                file_text = file.read().split('\n')
                file.close()

                for line in file_text:
                    commands = self.fmt.format_commands(line)

                    self.add_handler_options()
                    self.jobs.stop_dead()

                    self.execute.execute_command(commands)

        if do_shell:
            self.launch_history()
            self.launch_menu()

    def add_handler_options(self):
        handler_options = {
            'LHOST': {
                'Description': "Local host to listen on.",
                'Value': "0.0.0.0",
                'Type': "ip",
                'Required': True
            },
            'LPORT': {
                'Description': "Local port to listen on.",
                'Value': 8888,
                'Type': "port",
                'Required': True
            },
            'RBPORT': {
                'Description': "Remote bind port.",
                'Value': 8888,
                'Type': "port",
                'Required': True
            }
        }

        if self.modules.check_current_module():
            module = self.modules.get_current_module_name()
            current_module = self.modules.get_current_module_object()

            if module not in self.handler_options:
                self.handler_options[module] = handler_options

            if hasattr(current_module, "payload"):
                if 'BLINDER' not in current_module.options:
                    current_module.options.update({
                        'BLINDER': {
                            'Description': 'Use Blinder.',
                            'Value': 'yes' if self.payloads.get_current_payload() is None else 'no',
                            'Type': "boolean",
                            'Required': True
                        }
                    })

            required = True
            if 'BLINDER' in current_module.options:
                if current_module.options['BLINDER']['Value'].lower() in ['yes', 'y']:
                    required = False
                    current_module.payload['Value'] = None

            payload = self.payloads.get_current_payload()

            if hasattr(current_module, "payload"):
                current_module.options.update({
                    'PAYLOAD': {
                        'Description': 'Payload to use.',
                        'Value': current_module.payload['Value'],
                        'Type': "payload",
                        'Required': required
                    }
                })

            if payload is not None:
                if 'Handler' in current_module.payload:
                    if not current_module.payload['Handler']:
                        return

                current_module.options.update(self.handler_options[module])

                for option in current_module.options:
                    if option.lower() in ['lhost', 'lport', 'rbport']:
                        self.handler_options[module][option]['Value'] = current_module.options[option]['Value']

                if payload.details['Type'] == 'reverse_tcp':
                    for option in list(current_module.options):
                        if option.lower() in ['rbport']:
                            current_module.options.pop(option)

                elif payload.details['Type'] == 'bind_tcp':
                    for option in list(current_module.options):
                        if option.lower() in ['lhost', 'lport']:
                            current_module.options.pop(option)

                else:
                    for option in list(current_module.options):
                        if option.lower() in ['lhost', 'lport', 'rbport']:
                            current_module.options.pop(option)
            else:
                for option in list(current_module.options):
                    if option.lower() in ['lhost', 'lport', 'rbport']:
                        current_module.options.pop(option)
