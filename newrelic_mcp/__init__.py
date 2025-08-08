"""
New Relic MCP Server

A Model Context Protocol (MCP) server that provides programmatic access to New Relic APIs.
"""

__version__ = "1.0.0"
__author__ = "Caleb Piekstra"
__email__ = "calebpiekstra@gmail.com"

from .server import main

__all__ = ["main"]