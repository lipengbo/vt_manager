import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q

from project.models import Project, Membership, Category
from project.forms import ProjectForm
from invite.forms import ApplicationForm, InvitationForm
from invite.models import Invitation, Application

from resources.models import Switch
from communication.flowvisor_client import FlowvisorClient
from plugins.openflow.models import Flowvisor

@login_required
def index(request):
    user = request.user
    project_ids = Membership.objects.filter(user=user).values_list("project__id", flat=True)
    projects = Project.objects.filter(id__in=project_ids)
    context = {}
    context['projects'] = projects
    return render(request, 'project/index.html', context)

@login_required
def detail(request, id):
    project = get_object_or_404(Project, id=id)
    context = {}
    context['project'] = project
    return render(request, 'project/detail.html', context)

@login_required
def manage(request):
    user = request.user
    project_ids = Membership.objects.filter(user=user).values_list("project__id", flat=True)
    projects = Project.objects.filter(id__in=project_ids)
    context = {}
    context['projects'] = projects[:4]
    return render(request, 'project/manage.html', context)

@login_required
def invite(request, id):
    project = get_object_or_404(Project, id=id)
    if not (request.user == project.owner):
        return redirect('forbidden')
    context = {}
    context['project'] = project
    target_type = ContentType.objects.get_for_model(project)
    invited_user_ids = list(Invitation.objects.filter(target_id=project.id,
            target_type=target_type).values_list("to_user__id", flat=True))
    invited_user_ids.extend(project.member_ids())
    users = User.objects.exclude(id__in=set(invited_user_ids))
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            if len(query) > 256:
                query = query[:256]
            users = users.filter(username__icontains=query)
            context['query'] = query
    context['users'] = users

    if request.method == 'POST':
        user_ids = request.POST.getlist('user')
        message = request.POST.get('message')
        if message:
            for user_id in user_ids:
                user = get_object_or_404(User, id=user_id)
                form = InvitationForm({'message': message, 'to_user': user_id})
                if form.is_valid():
                    invitation = form.save(commit=False)
                    invitation.from_user = request.user
                    invitation.target = project
                    invitation.save()
        else:
            messages.add_message(request, messages.ERROR, _("Invitation message is required."))
    return render(request, 'project/invite.html', context)

@login_required
def apply(request):
    context = {}
    user = request.user
    projects = Project.objects.all()
    if 'category' in request.GET:
        cat_id = request.GET.get('category')
        if cat_id and cat_id != u'-1':
            current_cat = get_object_or_404(Category, id=cat_id)
            projects = projects.filter(category=current_cat)
            context['current_cat'] = current_cat
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            if len(query) > 256:
                query = query[:256]
            projects = projects.filter(Q(name__icontains=query)|Q(description__icontains=query))
            context['query'] = query
    categories = Category.objects.all()
    context['projects'] = projects
    context['categories'] = categories
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_id')
        message = request.POST.get('message')
        if message:
            for project_id in project_ids:
                project = get_object_or_404(Project, id=project_id)
                form = ApplicationForm({"to_user": project.owner.id, "message": message})
                if form.is_valid():
                    application = form.save(commit=False)
                    application.target = project
                    application.from_user = user
                    try:
                        application.save()
                    except IntegrityError:
                        pass
        else:
            messages.add_message(request, messages.ERROR, _("Application message is required."))
    return render(request, 'project/apply.html', context)

@login_required
@permission_required('project.add_project', login_url='/forbidden/')
def create_or_edit(request, id=None):
    user = request.user
    context = {}
    instance = None
    if id:
        instance = get_object_or_404(Project, id=id)
        island_ids = instance.slice_set.all().values_list('sliceisland__island__id', flat=True)
        print island_ids
        context['slice_islands'] = set(list(island_ids))
    if request.method == 'GET':
        form = ProjectForm(instance=instance)
    else:
        form = ProjectForm(request.POST, instance=instance)
        if form.is_valid():
            project = form.save(commit=False)
            category_name = request.POST.get('category_name')
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                category = Category(name=category_name)
                category.save()
            project.category = category
            project.owner = user
            project.save()
            form.save_m2m()
            return redirect('project_detail', id=project.id)

    context['form'] = form
    cats = Category.objects.all()
    context['cats'] = cats
    return render(request, 'project/create.html', context)

@login_required
def delete_member(request, id):
    user = request.user
    membership = get_object_or_404(Membership, id=int(id))
    project = membership.project
    if project.owner == user and not membership.is_owner:
        membership.delete()
    else:
        return redirect("forbidden")
    return redirect("project_detail", id=project.id)

@login_required
def delete_project(request, id):
    project = get_object_or_404(Project, id=id)
    if request.user == project.owner:
        try:
            project.delete()
        except Exception, e:
            messages.add_message(request, messages.ERROR, e)
    else:
        project.dismiss(request.user)
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    return redirect("project_index")

@login_required
def applicant(request, id):
    project = get_object_or_404(Project, id=id)
    if not (request.user == project.owner):
        return redirect('forbidden')
    target_type = ContentType.objects.get_for_model(project)
    applications = Application.objects.filter(target_id=project.id, target_type=target_type, accepted=False)
    context = {}
    context['applications'] = applications
    context['project'] = project

    if request.method == 'POST':
        application_ids = request.POST.getlist('application')
        selected_applications = Application.objects.filter(id__in=application_ids)
        for application in selected_applications:
            if 'approve' in request.POST:
                application.accept()
            elif 'deny' in request.POST:
                application.deny()

    return render(request, 'project/applicant.html', context)

def get_island_flowvisors(island_id=None):
    flowvisors = Flowvisor.objects.all()
    if island_id:
        flowvisors = flowvisors.filter(island__id=island_id)
    flowvisor_list = []
    for flowvisor in flowvisors:
        flowvisor_list.append({"host": flowvisor.ip + ":" + str(flowvisor.http_port), "id": flowvisor.id})
    return flowvisor_list

def get_all_cities():
    return [], 2,2,2,2,2

def topology(request):
    from resources.models import Switch
    root_controller = None
    no_parent = request.GET.get('no_parent')
    hide_filter = request.GET.get('hide_filter')
    island_id = request.GET.get('island_id', 0)
    show_virtual_switch = request.GET.get('show_virtual_switch')
    direct = request.GET.get('direct')
    try:
        island_id = int(island_id)
    except:
        island_id = 0
    flowvisors = get_island_flowvisors(island_id)

    all_gre_ovs = Switch.objects.filter(has_gre_tunnel=True)

    node_infos, total_server, total_switch, total_ctrl, total_nodes, total_island = get_all_cities()
    city_id = int(request.GET.get('city_id', 0))
    island_id = int(island_id)
    total_facility = 4

    #slices = get_slices()
    return render(request, 'topology/index.html', {
        'node_infos': node_infos,
        'city_id': city_id,
        'island_id': island_id,
        'total_server':total_server,
        'total_switch': total_switch,
        'total_ctrl': total_ctrl,
        'total_nodes': total_nodes,
        'total_island': total_island,
        'total_facility':total_facility,
        'all_gre_ovs': all_gre_ovs,
        'direct': direct,
        'no_parent': no_parent,
        'hide_filter': hide_filter,
        'show_virtual_switch':show_virtual_switch,
        #'slices': slices,
        'root_controllers': json.dumps(flowvisors)})

def swicth_desc(request, host, port, dpid):
    return HttpResponse(json.dumps({dpid:[]}), content_type="application/json")

def swicth_aggregate(request, host, port, dpid):
    return HttpResponse(json.dumps({dpid:[]}), content_type="application/json")

def device_proxy(request, host, port):
    return HttpResponse(json.dumps([]), content_type="application/json")

def links_proxy(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    links = flowvisor.link_set.all()
    link_data = []
    for link in links:
        if link.source.switch.island != flowvisor.island:
            continue
        if link.target.switch.island != flowvisor.island:
            continue
        link_data.append({
            "dst-port": link.target.port,
            "dst-port-name": link.target.name,
            "dst-switch": link.target.switch.dpid,
            "src-port": link.source.port,
            "src-port-name": link.source.name,
            "src-switch": link.source.switch.dpid
            })

    return HttpResponse(json.dumps(link_data), content_type="application/json")

@login_required
def links_direct(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    client = FlowvisorClient(host, port, flowvisor.password)
    data = client.get_links()
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def switch_direct(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    client = FlowvisorClient(host, port, flowvisor.password)
    data = json.dumps(client.get_switches())
    return HttpResponse(data, content_type="application/json")

@login_required
#@cache_page(60 * 60 * 24 * 10)
def switch_proxy(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    switch_ids_tuple = flowvisor.link_set.all().values_list('source__switch__id', 'target__switch__id')
    switch_ids = set()
    for switch_id_tuple in switch_ids_tuple:
        switch_ids.add(switch_id_tuple[0])
        switch_ids.add(switch_id_tuple[1])
    switches = Switch.objects.filter(id__in=switch_ids, island=flowvisor.island)
    switch_data = []
    for switch in switches:
        ports = switch.switchport_set.all()
        port_data = []
        for port in ports:
            port_data.append({"name": port.name, "portNumber": str(port.port), "db_id": port.id})
        switch_data.append({"dpid": switch.dpid, "db_name": switch.name, "ports": port_data})

    data = json.dumps(switch_data)
    return HttpResponse(data, content_type="application/json")
