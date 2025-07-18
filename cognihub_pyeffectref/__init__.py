"""
CogniHub PyEffectRef - A simplified implementation of Vue 3's ref/effect reactive system in Python

This package provides a reactive programming model similar to Vue 3's composition API,
allowing you to create reactive data containers (Ref) and effects that automatically
respond to data changes.
"""
from .ref import Ref
from .effect import effect

__all__ = ["Ref", "effect"]