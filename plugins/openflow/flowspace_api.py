# coding:utf-8
from models import *
from django.db import transaction
from slice.slice_exception import DbError
from plugins.openflow.models import FlowSpaceRule


import logging
LOG = logging.getLogger("CENI")


@transaction.commit_on_success
def flowspace_nw_add(slice_obj, old_nws, new_nm):
    """添加网段时添加flowspace
    """
    LOG.debug('flowspace_nw_add')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    if new_nm and (new_nm not in slice_obj.get_nws()):
        try:
            name = str(slice_obj.name) + '_df'
            nw_num = len(old_nws)
            if nw_num > 0:
                for i in range(nw_num):
                    create_default_flowspace(slice_obj, name, '100', '', '',
                        '', '', '', '0x800', old_nws[i], new_nm, '', '', '', '')
                    create_default_flowspace(slice_obj, name, '100', '', '',
                        '', '', '', '0x800', new_nm, old_nws[i], '', '', '', '')
            create_default_flowspace(slice_obj, name, '100', '', '',
                '', '', '', '0x800', new_nm, new_nm, '', '', '', '')
            create_default_flowspace(slice_obj, name, '100', '', '',
                '', '', '', '0x806', new_nm, new_nm, '', '', '', '')
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


def flowspace_nw_del(slice_obj, del_nw):
    """删除网段时删除相应flowspace
    """
    LOG.debug('flowspace_nw_del')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if del_nw and (del_nw in slice_obj.get_nws()):
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, '', '', del_nw, '')
        delete_default_flowspace(slice_obj, name, '', '', '', del_nw)
    return True


def flowspace_gw_add(slice_obj, new_gateway):
    """添加网关时添加flowspace
    """
    LOG.debug('flowspace_gw_add')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if new_gateway and (new_gateway not in slice_obj.get_gws()):
        name = str(slice_obj.name) + '_df'
        haved_nws = slice_obj.get_nws()
        for haved_nw in haved_nws:
            create_default_flowspace(slice_obj, name, '100', '', '',
                '', '', new_gateway, '0x800', haved_nw, '', '', '', '', '')
            create_default_flowspace(slice_obj, name, '100', '', '',
                '', new_gateway, '', '0x800', '', haved_nw, '', '', '', '')
    return True


def flowspace_gw_del(slice_obj, del_gateway):
    """删除网关时删除相应flowspace
    """
    LOG.debug('flowspace_gw_del')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if del_gateway and (del_gateway in slice_obj.get_gws()):
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, del_gateway, '', '', '')
        delete_default_flowspace(slice_obj, name, '', del_gateway, '', '')
    return True


def flowspace_dhcp_add(slice_obj, new_dhcp):
    """添加dhcp服务器时添加flowspace
    """
    LOG.debug('flowspace_dhcp_add')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if new_dhcp:
        dhcp_vm_macs = slice_obj.get_dhcp_vm_macs()
        if new_dhcp not in dhcp_vm_macs:
            name = str(slice_obj.name) + '_df'
            create_default_flowspace(slice_obj, name, '1', '', '',
                '', new_dhcp, '', '', '', '', '', '', '', '')
            haved_vms = slice_obj.get_vms()
            for haved_vm in haved_vms:
                if haved_vm.mac not in dhcp_vm_macs:
                    create_default_flowspace(slice_obj, name, '1', '', '',
                        '', str(haved_vm.mac), '', '', '', '', '', '', '', '')
    return True


def flowspace_dhcp_del(slice_obj, del_dhcp):
    """删除dhcp服务器时删除相应flowspace
    """
    LOG.debug('flowspace_dhcp_del')
    from CENI.Project.slice_api import get_slice_dhcps
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if del_dhcp:
        name = str(slice_obj.name) + '_df'
        delete_default_flowspace(slice_obj, name, del_dhcp, '', '', '')
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) == 0:
            haved_vms = slice_obj.get_vms()
            for haved_vm in haved_vms:
                delete_default_flowspace(slice_obj, name, str(haved_vm.mac), '', '', '')
    return True


def flowspace_vm_add(slice_obj, new_vm):
    """添加虚拟机时添加flowspace
    """
    LOG.debug('flowspace_vm_add')
    from CENI.Project.slice_api import get_slice_dhcps
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if new_vm:
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) != 0:
            name = str(slice_obj.name) + '_df'
            create_default_flowspace(slice_obj, name, '1', '', '',
                '', new_vm, '', '', '', '', '', '', '', '')
    return True


def flowspace_vm_del(slice_obj, del_vm):
    """删除虚拟机时删除相应flowspace
    """
    LOG.debug('flowspace_vm_del')
    from CENI.Project.slice_api import get_slice_dhcps
    try:
        Slice.objects.get(id=slice_obj.id)
    except Slice.DoesNotExist:
        return False
    if del_vm:
        haved_dhcps = get_slice_dhcps(slice_obj)
        if len(haved_dhcps) != 0:
            name = str(slice_obj.name) + '_df'
            delete_default_flowspace(slice_obj, name, del_vm, '', '', '')
    return True


def create_default_flowspace(slice_obj, name, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """创建默认flowspace
    """
    LOG.debug('create_default_flowspace')
    try:
        flowspace_obj = FlowSpaceRule(
            slice=slice_obj,
            name=name,
            priority=priority,
            in_port=in_port,
            dl_vlan=dl_vlan,
            dl_vpcp=dl_vpcp,
            dl_src=dl_src,
            dl_dst=dl_dst,
            dl_type=dl_type,
            nw_src=nw_src,
            nw_dst=nw_dst,
            nw_proto=nw_proto,
            nw_tos=nw_tos,
            tp_src=tp_src,
            tp_dst=tp_dst,
            is_default=1,
            actions=7)
        flowspace_obj.save()
    except Exception, ex:
        raise DbError(ex)
    else:
        return flowspace_obj


@transaction.commit_on_success
def delete_default_flowspace(slice_obj, name, dl_src, dl_dst, nw_src, nw_dst):
    """删除默认flowspace
    """
    LOG.debug('delete_default_flowspace')
    try:
        flowspace_objs = FlowSpaceRule.objects.filter(name=name, is_default=1)
        if dl_src:
            flowspace_objs = FlowSpaceRule.objects.filter(name=name,
                dl_src=dl_src, is_default=1)
        if dl_dst:
            flowspace_objs = FlowSpaceRule.objects.filter(name=name,
                dl_dst=dl_dst, is_default=1)
        if nw_src:
            flowspace_objs = FlowSpaceRule.objects.filter(name=name,
                nw_src=nw_src, is_default=1)
        if nw_dst:
            flowspace_objs = FlowSpaceRule.objects.filter(name=name,
                nw_dst=nw_dst, is_default=1)
        flowspace_objs.delete()
    except Exception, ex:
        transaction.rollback()


def matches_to_arg_match(in_port, dl_vlan, dl_vpcp, dl_src, dl_dst, dl_type,
    nw_src, nw_dst, nw_proto, nw_tos, tp_src, tp_dst):
    """将12个匹配相转化为flowspace的arg_match参数格式
    """
    LOG.debug('matches_to_arg_match')
    match = ''
    if in_port:
        match += 'in_port=' + in_port + ','
    if dl_vlan:
        match += 'dl_vlan=' + dl_vlan + ','
    if dl_vpcp:
        match += 'dl_vpcp=' + dl_vpcp + ','
    if dl_src:
        match += 'dl_src=' + dl_src + ','
    if dl_dst:
        match += 'dl_dst=' + dl_dst + ','
    if dl_type:
        match += 'dl_type=' + dl_type + ','
    if nw_src:
        match += 'nw_src=' + nw_src + ','
    if nw_dst:
        match += 'nw_dst=' + nw_dst + ','
    if nw_proto:
        match += 'nw_proto=' + nw_proto + ','
    if nw_tos:
        match += 'nw_tos=' + nw_tos + ','
    if tp_src:
        match += 'tp_src=' + tp_src + ','
    if tp_dst:
        match += 'tp_dst=' + tp_dst + ','
    if match == '':
        arg_match = 'any'
    else:
        ls = len(match)
        arg_match = match[0:ls - 1]
    return arg_match


def get_flowspace_topology(slice_obj):
    """获取slice的用户自定义flowspace拓扑信息
    """
    LOG.debug('get_flowspace_topology')


@transaction.commit_on_success
def create_user_flowspace(slice_obj, name, dpid, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """创建用户flowspace
    """
    LOG.debug('create_user_flowspace')


def edit_user_flowspace(flowspace_obj, dpid, priority, in_port, dl_vlan,
    dl_vpcp, dl_src, dl_dst, dl_type, nw_src, nw_dst, nw_proto, nw_tos, tp_src,
    tp_dst):
    """编辑用户flowspace
    """
    LOG.debug('edit_user_flowspace')


def delete_user_flowspace(flowspace_obj):
    """删除用户flowspace
    """
    LOG.debug('edit_user_flowspace')
    try:
        flowspace_obj.delete()
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)
