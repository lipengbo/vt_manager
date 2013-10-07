import urllib2
import urlparse
import sys
import getpass
import functools
import json
import pprint
import re
from optparse import OptionParser


def toInt(val):
    if val is None:
        return
    if val is not None and val.find('0x') != -1:
        return int(val, 16)
    return int(val)


def toStr(val):
    return str(val)


def getError(code):
    try:
        return ERRORS[code]
    except Exception, e:
        print "Unknown Error" + e
        return "error"

ERRORS = {
    -32700: "Parse Error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid Params",
    -32603: "Internal Error"
}

MATCHSTRS = {
    'in_port': ('in_port', toInt),
    'input_port': ('in_port', toInt),
    'dl_dst': ('dl_dst', toStr),
    'eth_dst': ('dl_dst', toInt),
    'dl_src': ('dl_src', toStr),
    'eth_src': ('dl_src', toInt),
    'dl_type': ('dl_type', toInt),
    'eth_type': ('dl_type', toInt),
    'dl_vlan': ('dl_vlan', toInt),
    'dl_vpcp': ('dl_vpcp', toInt),
    'dl_vlan_pcp': ('dl_vpcp', toStr),
    'nw_dst': ('nw_dst', toStr),
    'nw_src': ('nw_src', toStr),
    'nw_proto': ('nw_proto', toInt),
    'nw_tos': ('nw_tos', toInt),
    'tp_src': ('tp_src', toInt),
    'tp_dst': ('tp_dst', toInt)
}


def buildRequest(data, url, cmd):
    j = {"id": "fvctl", "method": cmd, "jsonrpc": "2.0"}
    h = {"Content-Type": "application/json"}
    if data is not None:
        j['params'] = data
    return urllib2.Request(url, json.dumps(j), h)


def parseResponse(data):
    j = json.loads(data)
    if 'error' in j:
        print "%s -> %s" % (getError(j['error']['code']), j['error']['message'])
        return ""
    return j['result']


def makeMatch(matchStr):
    if matchStr == 'any' or matchStr == 'all':
        return {}
    matchItems = matchStr.split(',')
    match = {}
    for item in matchItems:
        it = item.split('=')
        if len(it) != 2:
            print "Match items must be of the form <key>=<val>"
            return "error"
        try:
#             import pdb;pdb.set_trace()
            (mstr, func) = MATCHSTRS[it[0].lower()]
            match[mstr] = func(it[1])
        except KeyError, e:
            print "Unknown match item %s" % it[0] + e
            return "error"
    return match


def connect(cmd, data=None, flowvisor_url=None, flowvisor_ps=None):
    try:
        print data
        print flowvisor_url
        print flowvisor_ps
        #url = "https://192.168.28.141:8181"
        url = flowvisor_url
        ps = flowvisor_ps
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        #passman.add_password(None, url, "fvadmin", "cdn%nf")
        passman.add_password(None, url, "fvadmin", ps)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)

        req = buildRequest(data, url, cmd)
        ph = opener.open(req)
        return parseResponse(ph.read())
    except Exception, e:
        print 1
        print e
        if str(e) == '<urlopen error [Errno 104] Connection reset by peer>':
            return connect(cmd, data, flowvisor_url, flowvisor_ps)
        else:
            return ""
#         if e.code == 401:
#             print "Authentication failed: invalid password"
#         elif e.code == 504:
#             print "HTTP Error 504: Gateway timeout"
#         elif e.code == 500:
#             print "HTTP Error 500"
#         else:
#             print e
    except RuntimeError, e:
        print 2
        print e
        return ""


def do_addSlice(args, passwd, enabled, flowvisor_url, flowvisor_ps):
    print "Slice %s was successfully created" % args[0]
    return "success"


def do_updateSlice(args, opts, flowvisor_url, flowvisor_ps):
    print "Slice %s has been successfully updated" % args[0]
    return "success"


def do_removeSlice(args, flowvisor_url, flowvisor_ps):
    print "Slice %s has been deleted" % args[0]
    return "success"


def do_listSlices(flowvisor_url, flowvisor_ps):
    data = connect("list-slices", flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    print 'Configured slices:'
    for name in data:
        print '{0:15} --> {1:8}'.format(name['slice-name'], 'enabled' if name['admin-status'] else 'disabled')


def do_addFlowSpace(args, passwd, flowvisor_url, flowvisor_ps):
    print "Flowspace %s has been created." % args[0]
    return "success"


def do_updateFlowSpace(args, opts, flowvisor_url, flowvisor_ps):
    print "Flowspace %s has been updated." % args[0]
    return "success"


def do_removeFlowSpace(args, flowvisor_url, flowvisor_ps):
    print "Flowspace entries have been removed."
    return "success"


def do_listFlowSpace(flowvisor_url, flowvisor_ps):
    req = {}
    req['show-disabled'] = True
    ret = connect("list-flowspace", data=req, flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    if len(ret) == 0:
        print "  None"
    else:
        for item in ret:
            #print json.dumps(item, sort_keys=True, indent=1)
            print "\n"
        return ret


def do_listDatapathStats(dpid, flowvisor_url, flowvisor_ps):
    req = {"dpid": dpid}
    ret = connect("list-datapath-stats", data=req, flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    if len(ret) == 0:
        print "  None"
    else:
        print json.dumps(ret, sort_keys=True, indent=2)
        print "\n"
        return ret


def do_list_links(flowvisor_url, flowvisor_ps):
    ret = connect("list-links", data={}, flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    if len(ret) == 0:
        print "  None"
    else:
        return ret


def do_list_datapaths(flowvisor_url, flowvisor_ps):
    ret = connect("list-datapaths", data={}, flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    if len(ret) == 0:
        print "  None"
    else:
        return ret


def do_list_datapath_info(dpid, flowvisor_url, flowvisor_ps):
    ret = connect("list-datapath-info", data={'dpid': dpid}, flowvisor_url=flowvisor_url, flowvisor_ps=flowvisor_ps)
    if len(ret) == 0:
        print "  None"
    else:
        return ret


class FlowvisorClient(object):
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.url = 'https://{}:{}'.format(self.ip, self.port)

    def get_switches(self):
        datapaths = do_list_datapaths(self.url, self.password)
        switches = []
        if datapaths:
            for datapath in datapaths:
                switch = {'dpid': datapath}
                datapath_info = do_list_datapath_info(datapath, self.url, self.password)
                switch['ports'] = self._parse_datapath_info(datapath_info)
                switches.append(switch)
        return switches

    def _parse_datapath_info(self, info):
        if not info:
            return
        ports = []
        ports_info = zip(info['port-list'], info['port-names'])
        for port_info in ports_info:
            port_dict = {}
            port_dict['portNumber'] = port_info[0]
            port_dict['name'] = port_info[1]
            ports.append(port_dict)
        return ports

    def get_links(self):
        links_info = do_list_links(self.url, self.password)
        links = []
        if links_info:
            for link in links_info:
                link_dict = {}
                link_dict['dst-port'] = link['dstPort']
                link_dict['dst-switch'] = link['dstDPID']
                link_dict['src-port'] = link['srcPort']
                link_dict['src-switch'] = link['srcDPID']
                links.append(link_dict)
        return links
