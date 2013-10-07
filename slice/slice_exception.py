# coding:utf-8
# Filename:slice_exception.py
# Date:2013.9.12 9:30
# Author:Junxia Chen
import traceback
import logging
LOG = logging.getLogger("CENI")


class Error(Exception):

    def __init__(self, message=None):
        super(Error, self).__init__(message)


class ControllerUsedError(Error):

    def __init__(self, message='Unknown'):
        self.message = message
        super(ControllerUsedError, self).__init__('%s' % (message))


class DbError(Error):

    def __init__(self, message='Unknown'):
        self.message = message
        super(DbError, self).__init__('%s' % (message))


class NameExistError(Error):

    def __init__(self, message='Unknown'):
        self.message = message
        super(NameExistError, self).__init__('%s' % (message))


class FlowvisorError(Error):

    def __init__(self, message='Unknown'):
        self.message = message
        super(FlowvisorError, self).__init__('%s' % (message))


class IslandError(Error):

    def __init__(self, message='Unknown'):
        self.message = message
        super(FlowvisorError, self).__init__('%s' % (message))


def wrap_exception(f):
    def _wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception:
            LOG.error(traceback.print_exc())
            raise
    _wrap.func_name = f.func_name
    return _wrap