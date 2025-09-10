"""CLI command runner utilities"""

import asyncio
from typing import Any, Dict

class CLIRunner:
    """Handles CLI command execution"""
    
    def __init__(self):
        self.commands = {}
        
    async def run_command(self, command: str, args: Dict[str, Any]):
        """Execute a CLI command"""
        if command in self.commands:
            return await self.commands[command](**args)
        raise ValueError(f"Unknown command: {command}")
        
    def register_command(self, name: str, handler):
        """Register a new CLI command"""
        self.commands[name] = handler
