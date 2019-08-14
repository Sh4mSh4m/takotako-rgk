import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views import View
from django.template.defaulttags import register
from django.utils.decorators import method_decorator
from celery.result import AsyncResult
from time import sleep

from takotako.nornir2.takotako_main.inventory import Inventory
from takotako.nornir2.takotako_main.celery_tasks import orchestrate_simple, orchestrate_change
from django.contrib.auth.decorators import login_required


INVENTORY_INDEX = {}

#####################
# Support functions #
#####################


def initiates_inventory(user_id):
    """
    Support function to return existing inventory or creating one for user
    Inventories are stored in dict.
    Inventories are based on inventory class
    """
    try:
        inv = INVENTORY_INDEX[user_id]
    except KeyError:
        inv = Inventory()
        INVENTORY_INDEX[user_id] = inv
    finally:
        return inv


def shortens(inv):
    """
    Input is inventory
    Returns tuple of 3 items:
    - first N items from inv.pool and 
    - first N items ffrom inv.selection
    - whether there were wrongly formatted lines in inventory
    """
    max_lines = 2
    filtered_pool = {}
    filtered_selection = {}
    if 'failed_lines' in inv.pool:
        failed_pool = True
    else:
        failed_pool = False
    for host in inv.pool:
        if host != 'failed_lines':
            filtered_pool.update({host: inv.pool[host]})
            # only send the first 2 hosts
            if len(filtered_pool) == max_lines:
                filtered_pool.update({'stop': {}})
                break
    for host in inv.selection:
        filtered_selection.update({host: inv.selection[host]})
        if len(filtered_selection) == max_lines:
            filtered_selection.update({'stop': {}})
            break
    return filtered_pool, filtered_selection, failed_pool


def sorts_for_review(inv):
    """
    Input is inventory
    Returns tuple of 3:
    - failed_lines for review
    - pool per location with host names and ip (hostname key)
    - selection per location with host and interfaces
    """
    failed_lines = inv.pool.get('failed_lines',{})
    sorted_pool = {}
    sorted_selection = {}
    for host, specs in inv.pool.items():
        if host != 'failed_lines':
            # update pool
            location = specs['data']['location']
            ip = specs['hostname']
            if location in sorted_pool:
                sorted_pool[location].update({host: ip})
            # create key in pool
            else:
                sorted_pool[location] = {host: ip}
            if host in inv.selection:
                # update selection
                if location in sorted_selection:
                    sorted_selection[location].update(
                        {host: inv.selection[host]})
                # create key in selection
                else:
                    sorted_selection[location] = {
                        host: inv.selection[host]}
            else:
                pass
    return sorted_pool, sorted_selection, failed_lines


@register.filter
def keyvalue(dict, key):
    return dict[key]


#####################
#       Views       #
#####################


class InventoryView(View):
    @method_decorator(login_required(login_url='/accounts/login/'))
    def post(self, request):
        print('ok')
        if len(request.FILES) != 0:
            inv_file = request.FILES['inv_file']
            inv = initiates_inventory(request.user.id)
            # if file not with proper extension
            if not inv_file.name.endswith('.csv') and not inv_file.name.endswith('.tki'):
                print(f'File is not CSV type')
                return HttpResponseRedirect(reverse("network:index"))
            # if file is too large, return
            if inv_file.multiple_chunks():
                print(f"Uploaded file is too big (%.2f MB)." % (
                    inv_file.size/(1000*1000),))
                return HttpResponseRedirect(reverse("network:index"))
            if inv_file.name.endswith('.csv'):
                file_data = inv_file.read().decode("utf-8")
                # resets current pool and selection
                inv.pool = {}
                inv.selection = {}
                inv.load_csv(file_data)
            elif inv_file.name.endswith('.tki'):
                file_data = json.loads(inv_file.read().decode("utf-8"))
                # resets current pool and selection
                inv.pool = file_data['pool']
                inv.selection = file_data['selection']
            sleep(1)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            print('i got in second path')
            return HttpResponseRedirect(reverse("network:index"))

    @method_decorator(login_required(login_url='/accounts/login/'))
    def get(self, request):
        inv = initiates_inventory(request.user.id)
        if inv.pool != None:
            filtered_pool, filtered_selection, failed_pool = shortens(inv)
            if filtered_pool == {}:
                filtered_pool = None
            if filtered_selection == {}:
                filtered_selection = None
            return render(request, 'network/inventory.html', {'pool': filtered_pool, 'failed_pool': failed_pool, 'selection': filtered_selection})
        else:
            filtered_pool = None
            failed_pool = None
        return render(request, 'network/inventory.html', {'pool': filtered_pool, 'failed_pool': failed_pool, 'selection': inv.selection})


class SnapshotView(View):
    """
    User inventory is loaded
    Snapshot is only created to shoot and
    populate inv
    """

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        if data['order'] == 'shoot':
            order_list = data['values']
            inv = initiates_inventory(request.user.id)
            # Disabled for now to use custon hosts.yaml file
            # inv.export_nornir2
            celery_job = orchestrate_simple.delay(inv.pool, order_list)
            return JsonResponse({'celery_job_id': celery_job.id})

    def get(self, request):
        inv = initiates_inventory(request.user.id)
        return render(request, 'network/snapshot.html', {'inventory': inv.pool})


def poll_state(request):
    """
    Used to track asynced celery job
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        celery_job_id = data['celery_job_id']
        job = AsyncResult(celery_job_id)
        print(f"{job.state} {job.info}")
        if job.state == 'FAILURE':
            return JsonResponse({'status': 'FAILURE'})
        elif job.state != 'SUCCESS':
            return JsonResponse({'status': 'PENDING'})
        elif job.state == 'SUCCESS':
            inv = initiates_inventory(request.user.id)
            inv.pool.update(job.result)
            return JsonResponse({'status': 'SUCCESS'})
        else:
            return JsonResponse({'status': 'UNDEFINED'})


def testpage(request):
    return render(request, 'network/browser.html')


def browser(request):
    inv = initiates_inventory(request.user.id)
    inv_pool = inv.pool
    inv_selection = inv.selection
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if data['order'] == 'int_selection':
            # processes the post to id host and interface
            req_host, req_interface = data['host_interface'].split('&&')
            # processes to update inv and add modify the selected spec
            returned_int = {
                'host': req_host,
                'interface': req_interface,
                'module': inv_pool[req_host]['interfaces'][req_interface]['module'],
                'row': inv_pool[req_host]['interfaces'][req_interface]['row'],
                'selected': None
            }
            # if selection empty, add host no matter what
            # host will be removed before changes if no interface selected
            # and if no changes to be applied to it
            # in inv_selection check_before_change() method
            if req_host not in inv_selection:
                inv_selection.update({req_host: []})

            if req_interface in inv_selection[req_host]:
                returned_int['selected'] = False
                inv_selection[req_host].remove(req_interface)
            else:
                returned_int['selected'] = True
                inv_selection[req_host].append(req_interface)
            inv_selection[req_host].sort()
            return JsonResponse(returned_int)
        elif data['order'] == 'int_sh_run':
            req_host, req_interface = data['host_interface'].split('&&')
            returned_int = {
                'host': req_host,
                'interface': req_interface,
                'module': inv_pool[req_host]['interfaces'][req_interface]['module'],
                'runnning': inv_pool[req_host]['interfaces'][req_interface]['running'],
            }
            return JsonResponse(returned_int)
        elif data['order'] == 'filter':
            filters = data['filters']
            if 'running' in filters:
                # transform value into cleaned up list
                filters['running'] = [elt.strip()
                                      for elt in filters['running'].split('\n') if elt != '']
            print(filters)
            inv.filter(**filters)
            return JsonResponse({'result': 'ok'})
    # default view, should load pagination and inv pool for later
    else:
        tmp_switches_list = [{elt: inv_pool[elt]} for elt in inv_pool]
        page = request.GET.get('page')
        paginator = Paginator(tmp_switches_list, 2)
        switches_list = paginator.get_page(page)
        return render(request, 'network/browser.html', {'switches_list': switches_list, 'selection': inv_selection})


class ConfigView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        if data['order'] == 'config' and 'configs' in data:
            configs = data['configs']
            conf_lines = [elt.strip()
                          for elt in configs['configRunning'].split('\n') if elt != '']
            print(conf_lines)
            inv = initiates_inventory(request.user.id)
            # Disabled for now to use custon hosts.yaml file
            # inv.export_nornir2
            celery_job = orchestrate_change.delay(
                inv.pool, inv.selection, conf_lines)
            print('job launched')
            print(f'{celery_job.id}')
            return JsonResponse({'celery_job_id': celery_job.id})
        else:
            return JsonResponse({'result': 'Nok, JSON sent is incorrect'})

    def get(self, request):
        inv = initiates_inventory(request.user.id)
        return render(request, 'network/config.html', {'selection': inv.selection})


class ExportView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        inv = initiates_inventory(request.user.id)

        if data['order'] == 'export' and 'file_name' in data:
            tki_data = {}
            tki_data.update({'pool': inv.pool})
            tki_data.update({'selection': inv.selection})
            return JsonResponse(tki_data)
        else:
            return JsonResponse({'result': 'Nok, JSON sent is incorrect'})

    def get(self, request):
        return render(request, 'network/export.html')


class ReviewView(View):
    def get(self, request):
        inv = initiates_inventory(request.user.id)
        sorted_pool, sorted_selection, failed_lines = sorts_for_review(inv)
        return render(request, 'network/review.html', {'pool': sorted_pool, 'selection': sorted_selection, 'failed_lines': failed_lines})
