# coding:utf-8
from slice.models import Slice
from resources.models import Switch, VirtualSwitch, OVS_TYPE, SwitchPort
from slice.slice_exception import DbError
from plugins.openflow.flowspace_api import flowspace_gw_add, flowspace_gw_del
from django.db import transaction
import logging
LOG = logging.getLogger("CENI")
OVS_TYPE = {'NOMAL': 1, 'EXTERNAL': 2, 'RELATED': 3}


@transaction.commit_on_success
def slice_add_ovs_ports(slice_obj, ovs_ports):
    """slice添加交换端口
    """
    LOG.debug('slice_add_ovs_ports')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    try:
        for ovs_port in ovs_ports:
            slice_obj.add_resource(ovs_port)
            if ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                flowspace_gw_add(slice_obj, ovs_port.switch.virtualswitch.server.mac)
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


@transaction.commit_on_success
def slice_change_ovs_ports(slice_obj, ovs_ports):
    """slice更新交换端口
    """
    LOG.debug('slice_change_ovs_ports')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    try:
        haved_ovs_ports = slice_obj.get_switch_ports()
        cur_ovs_port_ids = []
        haved_ovs_port_ids = []
        for haved_ovs_port in haved_ovs_ports:
            haved_ovs_port_ids.append(haved_ovs_port.id)
        for ovs_port in ovs_ports:
            cur_ovs_port_ids.append(ovs_port.id)
            if ovs_port.id not in haved_ovs_port_ids:
                slice_obj.add_resource(ovs_port)
                if ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                    flowspace_gw_add(slice_obj, ovs_port.switch.virtualswitch.server.mac)
        for haved_ovs_port in haved_ovs_ports:
            if haved_ovs_port.id not in cur_ovs_port_ids:
                slice_obj.remove_resource(haved_ovs_port)
                if haved_ovs_port.switch.type() == OVS_TYPE['EXTERNAL']:
                    flowspace_gw_del(slice_obj, haved_ovs_port.switch.virtualswitch.server.mac)
    except Exception, ex:
        transaction.rollback()
        raise DbError(ex)


# def get_ovs_type(ovs):
#     """获取交换机类型，交换节点、虚拟机关联节点、网络出口节点
#     """
#     LOG.debug('get_ovs_type')
#     try:
#         dpid_lists = ovs.dpid.split(':')
#         if len(dpid_lists) > 2 and dpid_lists[0] == '7f' and dpid_lists[1] == 'ff':
#             return OVS_TYPE['RELATED']
#         if ovs.tag == 2:
#             return OVS_TYPE['EXTERNAL']
#         return OVS_TYPE['NOMAL']
#     except:
#         return OVS_TYPE['NOMAL']


def find_ovs_by_dpid(dpid):
    """通过dpid查找交换机记录，可能是switch或virtualswitch
    """
    LOG.debug('find_ovs_by_dpid')
    ovss = Switch.objects.filter(dpid=dpid)
    if ovss:
        if ovss[0].is_virtual():
            return ovss[0].virtualswitch
        else:
            return ovss[0]
    else:
        return None


def get_ovs_class(ovs):
    """通过dpid查找交换机记录，可能是Switch或VirtualSwitch
    """
    LOG.debug('get_ovs_class')
    return ovs.__class__.__name__
