# coding:utf-8
from slice.models import *
from project.models import Project
from slice.slice_exception import DbError, IslandError, NameExistError
from plugins.openflow.flowvisor_api import flowvisor_del_slice,\
    flowvisor_del_flowspace, flowvisor_add_flowspace,\
    flowvisor_update_slice_status, flowvisor_add_slice
from plugins.openflow.flowspace_api import matches_to_arg_match,\
    flowspace_nw_add, flowspace_nw_del
from plugins.openflow.controller_api import slice_change_controller,\
    slice_add_controller, delete_controller, create_add_controller
from resources.ovs_api import slice_add_ovs_ports
from plugins.ipam.models import IPUsage
from django.db import transaction
import time
import datetime

import logging
LOG = logging.getLogger("ccf")


def create_slice_step(project, name, description, island, user, ovs_ports, controller_info, slice_nw):
    slice_obj = None
    try:
        print 1
        slice_obj = create_slice_api(project, name, description, island, user)
        print 2
        slice_add_ovs_ports(slice_obj, ovs_ports)
        print 3
        create_add_controller(slice_obj, controller_info)
        print 4
        flowvisor_add_slice(island.flowvisor_set.all()[0], name, slice_obj.get_controller(), user.email)
        print 5
        IPUsage.objects.subnet_create_success(slice_obj.name)
        print 6
        flowspace_nw_add(slice_obj, [], slice_nw)
        print 7
#         创建并添加网段
#         创建并添加网关
#         创建并添加dhcp
#         创建并添加虚拟机
        return slice_obj
    except:
        print 8
        if slice_obj:
            print 9
            slice_obj.delete()
        print 10
        raise


@transaction.commit_on_success
def create_slice_api(project, name, description, island, user):
    """slice添加交换端口
    """
    print 'create_slice_api'
    try:
        Slice.objects.get(name=name)
    except Slice.DoesNotExist:
        if project and island and user:
            flowvisors = island.flowvisor_set.all()
            if flowvisors:
                date_now = datetime.datetime.now()
                date_delta = datetime.timedelta(seconds=5)
#                 date_delta = datetime.timedelta(days=30)
                print date_delta
                expiration_date = date_now + date_delta
                try:
                    slice_obj = Slice(owner=user,
                        name=name,
                        description=description,
                        project=project,
                        date_expired=expiration_date)
                    slice_obj.save()
                    slice_obj.add_island(island)
                    slice_obj.add_resource(flowvisors[0])
                    return slice_obj
                except Exception, ex:
                    transaction.rollback()
                    raise DbError(ex)
            else:
                raise IslandError("所选节点无可用flowvisor！")
        else:
            raise DbError("数据库异常!")
    else:
        raise NameExistError("slice名称已存在!")


@transaction.commit_on_success
def edit_slice_api(slice_obj, new_description, new_controller):
    """编辑slice，编辑描述信息、控制器、交换机端口
    """
    LOG.debug('edit_slice_api')
    try:
        slice_change_description(slice_obj, new_description)
        slice_change_controller(slice_obj, new_controller)
    except:
        raise


@transaction.commit_on_success
def slice_change_description(slice_obj, new_description):
    """编辑slice，编辑描述信息、控制器、交换机端口
    """
    LOG.debug('slice_change_description')
    if slice_obj:
        if slice_obj.description != new_description:
            try:
                slice_obj.change_description(new_description)
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)


@transaction.commit_on_success
def delete_slice_api(slice_obj):
    """删除slice
    """
    print 'delete_slice_api'
    if slice_obj:
        try:
#             删除虚拟机
#             删除dhcp
#             删除网关
#             删除slice网络地址
#             print 1
#             del_nw = slice_obj.get_nw()
#             print 2
#             flowspace_nw_del(slice_obj, del_nw)
            print 3
            try:
                IPUsage.objects.delete_subnet(slice_obj.name)
            except:
                pass
            print 4
#             删除底层slice
            flowvisor_del_slice(slice_obj.get_flowvisor(), slice_obj.name)
            print 5
#             删除控制器
            delete_controller(slice_obj.get_controller())
            print 6
#             删除交换机端口
#             删除slice记录
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)


@transaction.commit_on_success
def start_slice_api(slice_obj):
    """启动slice
    """
    LOG.debug('start_slice_api')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    else:
        if slice_obj.state == SLICE_STATE_STOPPED:
            try:
                slice_obj.start()
                flowvisor_update_slice_status(slice_obj.get_flowvisor(), slice_obj.name, True)
            except Exception:
                transaction.rollback()
                raise
            else:
                try:
                    update_slice_virtual_network(slice_obj)
                except:
                    pass


@transaction.commit_on_success
def stop_slice_api(slice_obj):
    """停止slice
    """
    LOG.debug('stop_slice_api')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        raise DbError(ex)
    else:
        if slice_obj.state == SLICE_STATE_STARTED:
            try:
                slice_obj.stop()
                flowvisor_update_slice_status(slice_obj.get_flowvisor(), slice_obj.name, False)
            except Exception:
                transaction.rollback()
                raise


def update_slice_virtual_network(slice_obj):
    """更新slice的虚网，添加或删除交换机端口、网段、gateway、dhcp、vm后调用
    """
    LOG.debug('update_slice_virtual_network')
    try:
        Slice.objects.get(id=slice_obj.id)
    except Exception, ex:
        return DbError(ex)
    flowvisor = slice_obj.get_flowvisor()
    flowspace_name = str(slice_obj.name) + '_df'
    try:
        flowvisor_del_flowspace(flowvisor, flowspace_name)
    except:
        raise
    switch_ports = slice_obj.get_switch_ports()
    default_flowspaces = slice_obj.get_default_flowspaces()
    for switch_port in switch_ports:
        for default_flowspace in default_flowspaces:
            in_port = str(switch_port.port)
            arg_match = matches_to_arg_match(
                in_port, default_flowspace.dl_vlan,
                default_flowspace.dl_vpcp, default_flowspace.dl_src,
                default_flowspace.dl_dst, default_flowspace.dl_type,
                default_flowspace.nw_src, default_flowspace.nw_dst,
                default_flowspace.nw_proto, default_flowspace.nw_tos,
                default_flowspace.tp_src, default_flowspace.tp_dst)
            try:
                flowvisor_add_flowspace(flowvisor, flowspace_name, slice_obj.name,
                    default_flowspace.actions, 'cdn%nf', switch_port.switch.dpid,
                    default_flowspace.priority, arg_match)
            except:
                raise


def get_slice_topology(slice_obj):
    """获取slice拓扑信息
    """
    LOG.debug('get_slice_topology')
#     交换机
    try:
        switches = []
        switch_dpids = []
        switch_ports = slice_obj.get_switch_ports()
        for switch_port in switch_ports:
            switch_dpids.append(switch_port.switch.dpid)
        switch_dpids = list(set(switch_dpids))
        for switch_dpid in switch_dpids:
            switch = {'dpid': switch_dpid}
            switches.append(switch)
    #     链接
        links = []
        flowvisor = slice_obj.get_flowvisor()
        if flowvisor:
            link_objs = flowvisor.link_set.filter(
                source__in=switch_ports, target__in=switch_ports)
        for link_obj in link_objs:
            link = {'src_switch': link_obj.source.switch.dpid,
                    'dst_switch': link_obj.target.switch.dpid}
            links.append(link)
    #     虚拟机
        specials = []
        normals = []
        servers = []
        virtual_switches = slice_obj.get_virtual_switches()
        for virtual_switch in virtual_switches:
            servers.append(virtual_switch.server)
        vms = slice_obj.get_vms()
        for vm in vms:
            virtual_switch = vm.server.get_link_vs()
            if virtual_switch:
                if vm.state == 1:
                    host_status = 1
                else:
                    host_status = 0
                if vm.type == 1:
                    vm_info = {'macAddress': vm.ip.ipaddr, 'switchDPID': virtual_switch.dpid,
                                'hostid': vm.id, 'hostStatus': host_status}
                    normals.append(vm_info)
        topology = {'switches': switches, 'links': links,
                    'normals': normals, 'specials': specials}
    except Exception, ex:
        return []
    else:
        return topology


def get_slice_resource(slice_obj):
    """获取slice资源，包括节点、flowvisor、控制器、交换机端口
    """
    LOG.debug('get_slice_resource')
