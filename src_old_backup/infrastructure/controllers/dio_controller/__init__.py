"""
Digital I/O Controller Package

This package contains digital I/O controller implementations for various hardware vendors.
"""

from .ajinextek import AjinextekDIOController

__all__ = ['AjinextekDIOController']