# coding:utf-8
from flowvisor_proxy import do_addSlice, do_updateSlice,\
    do_removeSlice, do_addFlowSpace, do_updateFlowSpace, do_removeFlowSpace
from slice.slice_exception import FlowvisorError, DbError
from django.contrib.auth.models import User as ceni_user

import logging
LOG = logging.getLogger("CENI")


def flowvisor_add_slice(flowvisor, slice_name, controller, user_email):
    """flowvisor上添加slice
    """
    LOG.debug('flowvisor_add_slice')
    if flowvisor and controller and user_email:
        controllerAdd = 'tcp:' + str(controller.ip) + ':' + str(controller.port) + ''
        args = [slice_name, controllerAdd, user_email]
        pwd = "cdn%nf"
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        adslice = do_addSlice(args, pwd, False, flowvisor_url, flowvisor_ps)
        if adslice == 'error':
            raise FlowvisorError("flowvisor上创建slice失败,flowvisor连接失败或控制器不可用!")
    else:
        raise DbError("数据库异常")


def flowvisor_update_sice_controller(flowvisor, slice_name, controller_ip, controller_port):
    """flowvisor上更新slice控制器
    """
    LOG.debug('flowvisor_update_sice_controller')
    if flowvisor and slice_name and controller_ip and controller_port:
            args = [str(slice_name)]
            opts = {'chost': str(controller_ip), 'cport': int(controller_port)}
            print opts
            flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
            flowvisor_ps = str(flowvisor.password)
            upslice = do_updateSlice(args, opts, flowvisor_url, flowvisor_ps)
            if upslice == 'error':
                raise FlowvisorError("flowvisor上更新控制器失败,flowvisor连接失败或控制器不可用!")
    else:
        raise DbError("数据库异常!")


def flowvisor_update_slice_status(flowvisor, slice_name, status):
    """flowvisor上更新slice启停状态
    """
    LOG.debug('flowvisor_update_slice_status')
    if flowvisor and slice_name:
        args = [str(slice_name)]
        opts = {'status': status}
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        upslice = do_updateSlice(args, opts, flowvisor_url, flowvisor_ps)
        if upslice == 'error':
            raise FlowvisorError("flowvisor更新slice状态失败!")
    else:
        raise DbError("数据库异常！")


def flowvisor_del_slice(flowvisor, slice_name):
    """flowvisor上删除slice
    """
    LOG.debug('flowvisor_del_slice')
    if flowvisor and slice_name:
        args = [str(slice_name)]
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        do_removeSlice(args, flowvisor_url, flowvisor_ps)
    else:
        raise DbError("数据库异常!")


def flowvisor_add_flowspace(flowvisor, name, slice_name, slice_action,
    pwd, dpid, priority, arg_match):
    """flowvisor上添加flowspace
    """
    LOG.debug('flowvisor_add_flowspace')
    if flowvisor:
        fsaction = '' + str(slice_name) + '=' + str(slice_action) + ''
        pwd = str(pwd)
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        dpid = str(dpid)
        name = str(name)
        priority = str(priority)
        arg_match = str(arg_match)
        args = [name, dpid, priority, arg_match, fsaction]
        adflowspace = do_addFlowSpace(args, pwd, flowvisor_url, flowvisor_ps)
        if adflowspace == 'error':
            raise FlowvisorError("flowvisor上添加flowspace失败！")
    else:
        raise DbError("数据库异常")


def flowvisor_update_flowspace(flowvisor, flowspace_name, priority_flag,
    arg_match_flag, priority, arg_match):
    """flowvisor上更新flowspace
    """
    LOG.debug('flowvisor_update_flowspace')
    opts = {}
    if flowvisor:
        if priority_flag == 1:
            opts['prio'] = priority
        if arg_match_flag == 1:
            opts['match'] = arg_match
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        args = [flowspace_name]
        upflowspace = do_updateFlowSpace(args, opts, flowvisor_url, flowvisor_ps)
        if upflowspace == 'error':
            raise FlowvisorError("flowvisor上更新flowspace失败！")
    else:
        raise DbError("数据库异常")


def flowvisor_del_flowspace(flowvisor, flowspace_name):
    """flowvisor上删除flowspace
    """
    LOG.debug('flowvisor_del_flowspace')
    if flowvisor:
        args = [flowspace_name]
        flowvisor_url = "https://" + str(flowvisor.ip) + ":" + str(flowvisor.http_port) + ""
        flowvisor_ps = str(flowvisor.password)
        do_removeFlowSpace(args, flowvisor_url, flowvisor_ps)
    else:
        raise DbError("数据库异常")
