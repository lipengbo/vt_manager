#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:utils.py
# Date:Fri Sep 13 17:46:30 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import functools
import time
import uuid
from plugins.ipam import netaddr

import os
import shlex
import signal
from eventlet.green import subprocess

from django.utils.translation import ugettext as _
import logging

LOG = logging.getLogger('plugins')


def _subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def subprocess_popen(args, stdin=None, stdout=None, stderr=None, shell=False,
                     env=None):
    return subprocess.Popen(args, shell=shell, stdin=stdin, stdout=stdout,
                            stderr=stderr, preexec_fn=_subprocess_setup,
                            close_fds=True, env=env)


def execute(cmd, root_helper=None, process_input=None, addl_env=None,
            check_exit_code=True, return_stderr=False):
    if root_helper:
        cmd = shlex.split(root_helper) + cmd
    cmd = map(str, cmd)

    LOG.debug(_("Running command: %s"), cmd)
    env = os.environ.copy()
    if addl_env:
        env.update(addl_env)
    obj = subprocess_popen(cmd, shell=False,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=env)

    _stdout, _stderr = (process_input and
                        obj.communicate(process_input) or
                        obj.communicate())
    obj.stdin.close()
    m = _("\nCommand: %(cmd)s\nExit code: %(code)s\nStdout: %(stdout)r\n"
          "Stderr: %(stderr)r") % {'cmd': cmd, 'code': obj.returncode,
                                   'stdout': _stdout, 'stderr': _stderr}
    #LOG.debug(m)
    if obj.returncode and check_exit_code:
        raise RuntimeError(m)
    return return_stderr and (_stdout, _stderr) or _stdout


def fetchfile(url, target):
    LOG.debug(_('Fetching %s') % url)
    execute(['curl', '--fail', url, '-o', target])


def gen_uuid():
    return str(uuid.uuid4())


def is_uuid_like(val):
    """For our purposes, a UUID is a string in canonical form:
        aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    """
    try:
        uuid.UUID(val)
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def timefunc(func):
    """Decorator that logs how long a particular function took to execute"""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            total_time = time.time() - start_time
            LOG.debug(_("timefunc: '%(name)s' took %(total_time).2f secs") %
                      dict(name=func.__name__, total_time=total_time))
    return inner


def generate_mac_address(ip):
    """Generate an Ethernet MAC address."""
    base_bin = netaddr.EUI('fa:16:00:00:00:00').value
    return str(netaddr.EUI(base_bin | netaddr.IPAddress(ip).value)).replace('-', ':')
