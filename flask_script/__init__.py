# coding=utf-8

from .core import Manager, Commands, Command


from .cli import prompt, prompt_pass, prompt_bool, prompt_choices

__author__ = 'GaoJie'
__all__ = ["manager", "Commands", "Command", "Option",
           "prompt", "prompt_pass", "prompt_bool", "prompt_choices"]

# 建立唯一的Manager实例
Manager.instance = manager = Manager()