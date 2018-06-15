#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class UnknownPair(Exception):
    def __init__(self, message="Unknown Name pair", errors=101, pairs=[]):
        # Call the base class constructor with the parameters it needs
        if pairs:
            pair = [ item.flag for item in pairs ]
            message = f" Pair is [" + ', '.join(pair) + "]\n" + message
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class MapApiException(Exception):
    def __init__(self, message="MapApiException", errors="20003"):
        # Call the base class constructor with the parameters it needs
        super().__init__("".join([message,f" ErrorCode:{errors}"]))

        # Now for your custom code...
        self.errors = errors

class ThirdPartyApiException(Exception):
    def __init__(self, message="ThirdPartyApiException", error_code=300001):
        # Call the base class constructor with the parameters it needs
        super().__init__("".join([message,f" ErrorCode:{error_code}"]))

        # Now for your custom code...
        self.error_code = error_code