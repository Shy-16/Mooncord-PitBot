# -*- coding: utf-8 -*-

## Command ##
# A reusable Command class to execute functionality with ease #


class Command:
    def __init__(self, module, permission='mod', dm_keywords=None):
        """
        @permissions: A minimum allowed permission to execute command.
        """
        self._bot = module._bot
        self._module = module
        self.permission = permission
        self.dm_keywords = dm_keywords or []

    async def execute(self, context):
        """Takes CommandContext and executes functionality"""

    async def dm(self, context):
        """Responds to a user DM of this command"""

    async def ping(self, context):
        """Responde to a user pinging the bot"""

    async def send_help(self, context):
        """Prints the help command"""

    async def send_no_permission_message(self, context):
        pass

def verify_permission(fn):
    """Verifies if the user is admin or mod"""
    async def inner(*args,**kwargs):
        command, context = args
        if command.permission == 'admin':
            if not context.is_admin:
                return
        elif command.permission == 'mod':
            if not (context.is_mod or context.is_admin):
                return
        await fn(*args,**kwargs)
        return
    return inner
