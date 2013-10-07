#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:undoManager.py
# Date:Mon Sep 23 14:31:57 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import contextlib
import sys
import logging

LOG = logging.getLogger('plugins')


@contextlib.contextmanager
def save_and_reraise_exception():
    """Save current exception, run some code and then re-raise.

    In some cases the exception context can be cleared, resulting in None
    being attempted to be reraised after an exception handler is run. This
    can happen when eventlet switches greenthreads or when running an
    exception handler, code raises and catches an exception. In both
    cases the exception context will be cleared.

    To work around this, we save the exception state, run handler code, and
    then re-raise the original exception. If another exception occurs, the
    saved exception is logged and the new exception is reraised.
    """
    type_, value, traceback = sys.exc_info()
    try:
        yield
    except Exception:
        # NOTE(jkoelker): Using LOG.error here since it accepts exc_info
        #                 as a kwargs.
        LOG.error('Original exception being dropped',
                  exc_info=(type_, value, traceback))
        raise
    raise type_, value, traceback


class UndoManager(object):

    """Provides a mechanism to facilitate rolling back a series of actions
    when an exception is raised.
    """
    def __init__(self):
        self.undo_stack = []

    def undo_with(self, undo_func):
        self.undo_stack.append(undo_func)

    def _rollback(self):
        for undo_func in reversed(self.undo_stack):
            undo_func()

    def rollback_and_reraise(self, msg=None):
        """Rollback a series of actions then re-raise the exception.

        .. note:: (sirp) This should only be called within an
                  exception handler.
        """
        with save_and_reraise_exception():
            if msg:
                LOG.exception(msg)
            self._rollback()
