# coding:utf-8
import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.contrib import messages

from slice.slice_api import create_slice_step, start_slice_api,\
    stop_slice_api, get_slice_topology, delete_slice_api, slice_change_description
from plugins.openflow.controller_api import slice_change_controller
from plugins.openflow.flowvisor_api import flowvisor_add_slice
from plugins.openflow.models import Controller
from resources.ovs_api import slice_add_ovs_ports
from project.models import Project, Island
from resources.models import SwitchPort
from slice.slice_exception import *
from plugins.ipam.models import IPUsage, Subnet

from slice.models import Slice

from plugins.vt.forms import VmForm
from resources.models import Server


@login_required
def create(request, proj_id):
    """创建slice。"""
    project = get_object_or_404(Project, id=proj_id)
    error_info = None
    islands = project.islands.all()
    if not islands:
        return render(request, 'slice/warning.html', {'info': '无可用节点，无法创建slice！'})
    ovs_ports = []
    for island in islands:
        switches = island.switch_set.all()
        for switch in switches:
            switch_ports = switch.switchport_set.all()
            if switch_ports:
                ovs_ports.append({'switch_type': switch.type(),
                    'switch': switch, 'switch_ports': switch_ports})
    vm_form = VmForm()
    context = {}
    context['project'] = project
    context['islands'] = islands
    context['ovs_ports'] = ovs_ports
    context['error_info'] = error_info
    context['vm_form'] = vm_form
    return render(request, 'slice/create_slice.html', context)


@login_required
def create_first(request, proj_id):
    """创建slice不含虚拟机创建。"""
    project = get_object_or_404(Project, id=proj_id)
    if request.method == 'POST':
        try:
            user = request.user
            slice_name = request.POST.get("slice_name")
            slice_description = request.POST.get("slice_description")
            island_id = request.POST.get("island_id")
            island = get_object_or_404(Island, id=island_id)
            controller_type = request.POST.get("controller_type")
            if controller_type == 'default_create':
                controller_sys = request.POST.get("controller_sys")
                controller_info = {'controller_type': controller_type,
                                   'controller_sys': controller_sys}
            else:
                controller_ip = request.POST.get("controller_ip")
                controller_port = request.POST.get("controller_port")
                controller_info = {'controller_type': controller_type,
                                   'controller_ip': controller_ip,
                                   'controller_port': controller_port}
            port_ids = []
            switch_port_ids_str = request.POST.get("switch_port_ids")
#             print switch_port_ids_str
            switch_port_ids = switch_port_ids_str.split(',')
            for switch_port_id in switch_port_ids:
                port_ids.append(int(switch_port_id))
            ovs_ports = SwitchPort.objects.filter(id__in=port_ids)
            slice_nw = request.POST.get("slice_nw")
            slice_obj = create_slice_step(project, slice_name,
                slice_description, island, user, ovs_ports, controller_info, slice_nw)
        except Exception, ex:
            jsondatas = {'result': 0, 'error_info': str(ex)}
        else:
            jsondatas = {'result': 1, 'slice_id': slice_obj.id}
        result = json.dumps(jsondatas)
        return HttpResponse(result, mimetype='text/plain')


@login_required
def list(request, proj_id):
    """显示所有slice。"""
    project = get_object_or_404(Project, id=proj_id)
    context = {}
    context['project'] = project
    context['slices'] = project.slice_set.all()
    return render(request, 'slice/slice_list.html', context)


@login_required
def edit_description(request, slice_id):
    """编辑slice描述信息。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if request.method == 'POST':
        slice_description = request.POST.get("slice_description")
        try:
            slice_change_description(slice_obj, slice_description)
        except Exception, ex:
            messages.add_message(request, messages.ERROR, ex)
    return HttpResponseRedirect(
        reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


@login_required
def edit_controller(request, slice_id):
    """编辑slice控制器。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    if request.method == 'POST':
        controller_type = request.POST.get("controller_type")
        if controller_type == 'default_create':
            controller_sys = request.POST.get("controller_sys")
            controller_info = {'controller_type': controller_type,
                               'controller_sys': controller_sys}
        else:
            controller_ip_port = request.POST.get("controller_ip_port").split(':')
            controller_info = {'controller_type': controller_type,
                               'controller_ip': controller_ip_port[0],
                               'controller_port': controller_ip_port[1]}
        try:
            slice_change_controller(slice_obj, controller_info)
        except Exception, ex:
            messages.add_message(request, messages.ERROR, ex)
    return HttpResponseRedirect(
        reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


@login_required
def detail(request, slice_id):
    """编辑slice。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    context = {}
    context['slice_obj'] = slice_obj
    context['island'] = slice_obj.get_island()
    context['controller'] = slice_obj.get_controller()
    context['flowvisor'] = slice_obj.get_flowvisor()
    context['gws'] = []
    context['dhcps'] = []
    context['vms'] = slice_obj.get_common_vms()
    context['check_vm_status'] = 0
    if slice_obj.state == 1:
        all_vms = slice_obj.get_vms()
        for vm in all_vms:
            if vm.state == 8:
                context['check_vm_status'] = 1
                break
    return render(request, 'slice/slice_detail.html', context)


@login_required
def delete(request, slice_id, flag):
    """删除slice。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    project_id = slice_obj.project.id
    if request.user == slice_obj.owner:
        try:
            slice_obj.delete()
        except Exception, ex:
            messages.add_message(request, messages.ERROR, ex)
    else:
        return redirect("forbidden")
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    if int(flag) == 1:
        return HttpResponseRedirect(
            reverse("project_detail", kwargs={"id": project_id}))
    else:
        return HttpResponseRedirect(
            reverse("slice_list", kwargs={"proj_id": project_id}))


@login_required
def start_or_stop(request, slice_id, flag):
    """启动或停止slice。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    try:
        if int(flag) == 1:
            start_slice_api(slice_obj)
        else:
            stop_slice_api(slice_obj)
    except Exception, ex:
        messages.add_message(request, messages.ERROR, ex)
    return HttpResponseRedirect(
        reverse("slice_detail", kwargs={"slice_id": slice_obj.id}))


def topology(request, slice_id):
    """ajax获取slice拓扑信息。"""
    slice_obj = get_object_or_404(Slice, id=slice_id)
    jsondatas = get_slice_topology(slice_obj)
    print jsondatas
    result = json.dumps(jsondatas)
    return HttpResponse(result, mimetype='text/plain')


@login_required
def check_slice_name(request, slice_name):
    """
    校验用户所填slice名称是否已经存在
    return:
        value:
          slice名称已存在:value = 1
          slice名称不存在：value = 0
    """
    slice_objs = Slice.objects.filter(name=slice_name)
    if slice_objs:
        return HttpResponse(json.dumps({'value': 1}))
    else:
        return HttpResponse(json.dumps({'value': 0}))


@login_required
def create_nw(request, owner, nw_num):
    """
    分配slice网段
    return:
        value:
          失败:value = 0
          成功：value = 网段（192.168.5.6/27）
    """
    try:
        nw_objs = Subnet.objects.filter(owner=owner)
        if nw_objs:
            IPUsage.objects.delete_subnet(owner)
        print "net work 1"
        nw = IPUsage.objects.create_subnet(owner, int(nw_num), 1800)
        print "net work 2"
        if nw:
            print "net work 3"
            return HttpResponse(json.dumps({'value': nw}))
        else:
            print "net work 4"
            return HttpResponse(json.dumps({'value': 0}))
    except Exception, ex:
        print "net work 5"
        print ex
        return HttpResponse(json.dumps({'value': 0}))


@login_required
def delete_nw(request, owner):
    """
    删除slice网段
    return:
        value:
          失败:value = 0
          成功：value = 1
    """
    try:
        if IPUsage.objects.delete_subnet(owner):
            return HttpResponse(json.dumps({'value': 1}))
        else:
            return HttpResponse(json.dumps({'value': 0}))
    except:
        return HttpResponse(json.dumps({'value': 0}))


def get_show_slices(request):
    """ajax获取首页展示slice。"""
    slice_objs = Slice.objects.all()
    slices = []
    for slice_obj in slice_objs:
        slice_show = {'id': slice_obj.id, 'name': slice_obj.get_show_name()}
        slices.append(slice_show)
    return HttpResponse(json.dumps({'slices': slices}))
