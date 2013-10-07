#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:exception.py
# Date:Mon Sep 16 09:06:07 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.
import functools
import sys
from django.utils.translation import ugettext as _


class ProcessExecutionError(IOError):

    def __init__(self, stdout=None, stderr=None, exit_code=None, cmd=None,
                 description=None):
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        self.cmd = cmd
        self.description = description

        if description is None:
            description = _('Unexpected error while running command.')
        if exit_code is None:
            exit_code = '-'
        message = _('%(description)s\nCommand: %(cmd)s\n'
                    'Exit code: %(exit_code)s\nStdout: %(stdout)r\n'
                    'Stderr: %(stderr)r') % locals()
        IOError.__init__(self, message)


def wrap_exception(notifier=None, publisher_id=None, event_type=None,
                   level=None):
    def inner(f):
        def wrapped(*args, **kw):
            try:
                return f(*args, **kw)
            except Exception as e:
                # Save exception since it can be clobbered during processing
                # below before we can re-raise
                exc_info = sys.exc_info()

                if notifier:
                    payload = dict(args=args, exception=e)
                    payload.update(kw)

                    # Use a temp vars so we don't shadow
                    # our outer definitions.
                    temp_level = level
                    if not temp_level:
                        temp_level = notifier.ERROR

                    temp_type = event_type
                    if not temp_type:
                        # If f has multiple decorators, they must use
                        # functools.wraps to ensure the name is
                        # propagated.
                        temp_type = f.__name__

                    notifier.notify(publisher_id, temp_type, temp_level,
                                    payload)

                # re-raise original exception since it may have been clobbered
                raise exc_info[0], exc_info[1], exc_info[2]

        return functools.wraps(f)(wrapped)
    return inner


class Error(Exception):
    pass


class CCFException(Exception):

    """
    Base Exception
    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass
        if not message:
            try:
                message = self.message % kwargs
            except:
                message = self.message
        super(CCFException, self).__init__(message)


class ImagePaginationFailed(CCFException):
    message = _("Failed to paginate through images from image service")


class VirtualInterfaceCreateException(CCFException):
    message = _("Virtual Interface creation failed")


class VirtualInterfaceMacAddressException(CCFException):
    message = _("5 attempts to create virtual interface"
                "with unique mac address failed")


class GlanceConnectionFailed(CCFException):
    message = _("Connection to glance failed") + ": %(reason)s"


class Invalid(CCFException):
    message = _("Unacceptable parameters.")
    code = 400


class InvalidCidr(Invalid):
    message = _("Invalid cidr %(cidr)s.")


class InstanceNotRunning(Invalid):
    message = _("Instance %(instance_id)s is not running.")


class InstanceNotSuspended(Invalid):
    message = _("Instance %(instance_id)s is not suspended.")


class InstanceNotInRescueMode(Invalid):
    message = _("Instance %(instance_id)s is not in rescue mode")


class InstanceSuspendFailure(Invalid):
    message = _("Failed to suspend instance") + ": %(reason)s"


class InstanceResumeFailure(Invalid):
    message = _("Failed to resume server") + ": %(reason)s."


class InstanceRebootFailure(Invalid):
    message = _("Failed to reboot instance") + ": %(reason)s"


class InstanceTerminationFailure(Invalid):
    message = _("Failed to terminate instance") + ": %(reason)s"


class ServiceUnavailable(Invalid):
    message = _("Service is unavailable at this time.")


class DestinationHostUnavailable(Invalid):
    message = _("Destination compute host is unavailable at this time.")


class SourceHostUnavailable(Invalid):
    message = _("Original compute host is unavailable at this time.")


class InvalidHypervisorType(Invalid):
    message = _("The supplied hypervisor type of is invalid.")


class InvalidDiskFormat(Invalid):
    message = _("Disk format %(disk_format)s is not acceptable")


class InvalidIpAddressError(Invalid):
    message = _("%(address)s is not a valid IP v4/6 address.")


class NotFound(CCFException):
    message = _("Resource could not be found.")
    code = 404


class ImageNotFound(NotFound):
    message = _("Image %(image_id)s could not be found.")


class NetworkNotFound(NotFound):
    message = _("Network %(network)s could not be found.")


class NetworkNotFoundForBridge(NetworkNotFound):
    message = _("Network could not be found for bridge %(bridge)s")


class NetworkNotFoundForUUID(NetworkNotFound):
    message = _("Network could not be found for uuid %(uuid)s")


class NetworkNotFoundForCidr(NetworkNotFound):
    message = _("Network could not be found with cidr %(cidr)s.")


class NetworkNotFoundForInstance(NetworkNotFound):
    message = _("Network could not be found for instance %(instance_id)s.")


class NoNetworksFound(NotFound):
    message = _("No networks defined.")


class NetworkInUse(CCFException):
    message = _("Network %(network)s is still in use.")


class NetworkNoMoreSubNet(CCFException):
    message = _("%(network)s is required to create a network.")


class FlavorNotFound(NotFound):
    message = _("Flavor %(flavor_id)s could not be found.")


class ClassNotFound(NotFound):
    message = _("Class %(class_name)s could not be found: %(exception)s")


class FileNotFound(NotFound):
    message = _("File %(file_path)s could not be found.")
