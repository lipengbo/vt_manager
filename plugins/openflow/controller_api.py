# coding:utf-8
from slice.models import Slice
from plugins.openflow.models import Controller
from slice.slice_exception import DbError, ControllerUsedError
from flowvisor_api import flowvisor_update_sice_controller
from django.db import transaction
from plugins.vt.api import create_vm_for_controller, delete_vm_for_controller
import logging
LOG = logging.getLogger("CENI")


@transaction.commit_on_success
def create_add_controller(slice_obj, controller_info):
    """创建并添加slice控制器
    """
    if slice_obj:
        try:
            if controller_info['controller_type'] == 'default_create':
                controller = create_default_controller(slice_obj,
                    controller_info['controller_sys'])
                controller = slice_obj.project.islands.all()[0].controller_set.all()[0]
            else:
                controller = create_user_defined_controller(slice_obj,
                    controller_info['controller_ip'],
                    controller_info['controller_port'])
            slice_add_controller(slice_obj, controller)
        except Exception, ex:
            transaction.rollback()
            raise
    else:
        raise DbError("数据库异常")


@transaction.commit_on_success
def slice_add_controller(slice_obj, controller):
    """slice添加控制器
    """
    LOG.debug('slice_add_controller')
    if slice_obj and controller:
        if controller.is_used():
            raise ControllerUsedError('控制器已经被使用！')
        if not slice_obj.get_controller():
            try:
                slice_obj.add_resource(controller)
            except Exception, ex:
                transaction.rollback()
                raise DbError(ex)
    else:
        raise DbError("数据库异常")


@transaction.commit_on_success
def create_user_defined_controller(slice_obj, controller_ip, controller_port):
    """创建用户自定义控制器记录
    """
    if slice_obj:
        try:
            controller = Controller(
                name='user_define',
                ip=controller_ip,
                port=int(controller_port),
                http_port=0,
                state=1,
                island=slice_obj.get_island())
            controller.save()
            return controller
        except Exception, ex:
            transaction.rollback()
            raise DbError(ex)
    else:
        raise DbError("数据库异常")


#@transaction.commit_on_success
def create_default_controller(slice_obj, controller_sys):
    """创建默认控制器
    """
    if slice_obj:
        try:
            #调用控制器创建接口
            #controller = Controller(
                #name=controller_sys,
                #ip='192.168.8.9',
                #port=7687,
                #http_port=0,
                #state=1,
                #island=slice_obj.get_island())
            island = slice_obj.get_island()
            #先创建虚拟机然后再创建controller
            vm, ip = create_vm_for_controller(island_obj=island, slice_obj=slice_obj, image_name=controller_sys)
            controller = Controller(name=controller_sys, port=6633, http_port=0, state=1, island=island)
            controller.ip = ip
            controller.host = vm
            controller.save()
            return controller
        except Exception, ex:
            #transaction.rollback()
            import traceback
            print traceback.print_exc()
            raise DbError(ex)
    else:
        raise DbError("数据库异常")


def delete_controller(controller):
    """创建用户自定义控制器记录
    """
    if controller:
        if controller.name == 'user_define' and (not controller.host):
            controller.delete()
        else:
            #先删除虚拟机然后删除controller记录
            delete_vm_for_controller(controller.host)
            controller.delete()


@transaction.commit_on_success
def slice_change_controller(slice_obj, controller_info):
    """slice更改控制器
    """
    LOG.debug('slice_change_controller')
    if slice_obj:
        try:
            haved_controller = slice_obj.get_controller()
            if controller_info['controller_type'] == 'default_create':
                if haved_controller.name != controller_info['controller_sys']:
                    delete_controller(haved_controller)
                    create_add_controller(slice_obj, controller_info)
                    controller = slice_obj.get_controller()
                    flowvisor_update_sice_controller(slice_obj.get_flowvisor(),
                        slice_obj.name, controller.ip, controller.port)
            else:
                if haved_controller.ip != controller_info['controller_ip'] or haved_controller.port != int(controller_info['controller_port']):
                    haved_controller.ip = controller_info['controller_ip']
                    haved_controller.port = int(controller_info['controller_port'])
                    haved_controller.save()
                    flowvisor_update_sice_controller(slice_obj.get_flowvisor(),
                        slice_obj.name, haved_controller.ip, haved_controller.port)
        except:
            transaction.rollback()
            raise
    else:
        raise DbError("数据库异常")
