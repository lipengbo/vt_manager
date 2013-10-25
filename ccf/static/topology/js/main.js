/*
   Copyright 2012 IBM

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/


var STATIC_URL = '/site_media/static/';
var svg;
var force;
var g_nodes = [];
var g_links = [];
var width = 700,
    height = 400;

var color = d3.scale.category20();
var g_nodes_map = {};
var g_links_map = {};
var nodes_map = {};
var origin_nodes_map = {};
var mousedown_node = null;
var tooltip = CustomTooltip( "posts_tooltip", 240 );
force = d3.layout.force()
    .linkDistance(function(d){
            var distance = 100;
            if (d.info) {
                distance = 100;
            }
            if (d.type) {
                distance = 200;
            }
            return distance;
        })
         .charge(function(d){
             var charge = -1500;
             if(d.group == 1) {
                chrage = -1500;
             }
             if (d.type) {
                charge = -20;
             }
             return charge})
         .size([width, height]);
svg_obj = d3.select("#topology-svg").append("svg")
            .attr("width", width)
            .attr("height", height);
var svg = svg_obj.append('g')
    .call(d3.behavior.zoom().on("zoom", rescale))
    .on("dblclick.zoom", null)
    .append('g')
    .attr('class', 'wrap')
    .on("mouseup", mouseup)
    .on("mousedown", mousedown);
svg.append('rect')
    .attr('width', "100%")
    .attr('height', "100%")
    .attr('fill', 'white');
var bandwidth_capacities = ['10M', '100M', '1G', '10G'];
var gre_ovs_capacity = [];
for (var i = 0; i < gre_ovses.length; i++) {
    gre_ovs_capacity.push(bandwidth_capacities[Math.floor(Math.random() * 4)]);
};
function rescale() {
    
  if(d3.event.ctrlKey || mousedown_node) return;
  trans=d3.event.translate;
  scale=d3.event.scale;

  svg.attr("transform",
      "translate(" + trans + ")"
      + " scale(" + scale + ")");
}
function mouseup () {
    mousedown_node = null;
}
function mousedown() {
  // prevent I-bar on drag
  //d3.event.preventDefault();
  
  // because :active only works in WebKit?

  if(d3.event.ctrlKey || mousedown_node) return;

  
    svg.call(d3.behavior.zoom().on("zoom", rescale))
}
var AppRouter = Backbone.Router.extend({

    routes:{
        "":"home",
        "topology":"topology",
        "switches":"switchList",
        "switch/:id":"switchDetails",
        "switch/:id/port/:p":"portDetails", // not clear if needed
        "hosts":"hostList",
        "host/:id":"hostDetails",
        // "vlans":"vlanList" // maybe one day
        // "vlan/:id":"vlanDetails"
    },

    initialize:function () {
        this.headerView = new HeaderView();
        $('.header').html(this.headerView.render().el);

        // Close the search dropdown on click anywhere in the UI
        $('body').click(function () {
            $('.dropdown').removeClass("open");
        });
    },

    home:function () {
        $('#content').html(new HomeView().render().el);
        $('ul[class="nav"] > li').removeClass('active');
        $('a[href="/"]').parent().addClass('active');
    },

    topology:function (island) {
        //hackBase = "/" + controller_host;
        //console.log("switching to topology view");
        var topo = new Topology({hackBase:island.hackBase, island:island});
        var wrap = $('#island' + island.id);
        if (wrap.length == 0) {
            wrap = $('<div id="island' + island.id + '"></div>');
            $('#content').append(wrap);
        }
        var topology_view = new TopologyView({model:topo, hosts:island.hl});
        island.topology_view = topology_view;
        wrap.html(topology_view.render().el);
        // TODO factor this code out
        $('ul.nav > li').removeClass('active');
        $('li > a[href*="topology"]').parent().addClass('active');
    },
    
    switchDetails:function (id) {
        //console.log("switching [sic] to single switch view");
        var sw = swl.get(id);
        $('#content').html(new SwitchView({model:sw}).render().el);
        $('ul.nav > li').removeClass('active');
        $('li > a[href*="/switches"]').parent().addClass('active');
    },
    
    switchList:function () {
        //console.log("switching [sic] to switch list view");
        $('#content').html(new SwitchListView({model:swl}).render().el);
        $('ul.nav > li').removeClass('active');
        $('li > a[href*="/switches"]').parent().addClass('active');
    },

    hostDetails:function (id) {
        //console.log("switching to single host view");
        var h = hl.get(id);
        $('#content').html(new HostView({model:h}).render().el);
        $('ul.nav > li').removeClass('active');
        $('li > a[href*="/hosts"]').parent().addClass('active');
    },
    
    hostList:function () {
        //console.log("switching to host list view");
        $('#content').html(new HostListView({model:hl}).render().el);
        $('ul.nav > li').removeClass('active');
        $('li > a[href*="/hosts"]').parent().addClass('active');
    },

});

// load global models and reuse them

var updating = true;
 var drag = d3.behavior.drag()
        .on("dragstart", function(d) {
            this.__origin__ = [d.x, d.y];
            force.on('tick', null);
        })
        .on("drag", function(d,i) {
            d.x = Math.min(width, Math.max(0, this.__origin__[0] += d3.event.dx));
            d.y = Math.min(height, Math.max(0, this.__origin__[1] += d3.event.dy));
            init_svg();
            force.on('tick', null);
            svg.selectAll(".node")
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
            svg.selectAll(".link").attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
        }).on("dragend", function() {
            delete this.__origin__;
        });


var init_count = 0;
function recompose_dpid(dpid) {
    return dpid;
    var new_dpid = "";
    for (var i = 0; i < dpid.length; i+=2) {
        if (i != 0) {
            new_dpid += ":";
        }
        new_dpid += dpid[i] + dpid[i+1];
    };
    return new_dpid;
}
function highlight( data, i, element ) {
    //d3.select( element ).attr( "stroke", "black" );

    var d = data;
    var content = "";
    
    if (data.id in origin_nodes_map) {
        var origin_data = origin_nodes_map[data.id];
        
        if (!origin_data.ports) {
            return;
        }
        content += "<h6>" + data.id + "</h6>";
        content += "<table class='table'>" + 
            "<tr><th>端口</th>" + 
            "</tr>";
        $.each(origin_data.ports, function(index, port){
            var state = port.state == 1 ? "活跃" : "非活跃";
            content += "<tr><td>"; 
                        content += d.db_name + ":" + port.name + "(" + port.portNumber+ ")";
                        var port_pairs = {};
                        $.each(g_links_map[d.island_id], function(index, link) {
                            var port_pair_key = [port.portNumber, link.info['dst-port-name']].sort().join('');
                            if (port_pair_key in port_pairs) {
                                return;
                            }
                            if ((link.source.id == d.id) && (link.info['src-port'] == port.portNumber)) {
                                port_pairs[port_pair_key] = '';
                                content += ' <-----> ' + link.target.db_name + ":" + link.info['dst-port-name'] + "(" + link.info['dst-port'] + ")";
                            }
                            port_pair_key = [port.portNumber, link.info['src-port-name']].sort().join('');
                            if (port_pair_key in port_pairs) {
                                return;
                            }
                            if ((link.target.id == d.id) && (link.info['dst-port'] == port.portNumber)) {
                                port_pairs[port_pair_key] = '';
                                content += ' <-----> ' + link.source.db_name + ":" + link.info['src-port-name'] + "(" + link.info['src-port'] + ")";
                            }
                        });
                        content += "</td></tr>";
        });
        content += "</table>";
        tooltip.showTooltip(content, d3.event);
    } else {
        if (data.source.group == 1 && data.target.group == 1 && data.info) {
            content += "源端口：" + data.info['src-port'] + " <br> 目的端口：" + data.info['dst-port'] ;
            tooltip.showTooltip(content, d3.event);
        } else if (data.type)  {
            content += "带宽使用：" + data.bandwidth + data.capacity.slice(data.capacity.length - 1) + "/" + data.capacity;
            tooltip.showTooltip(content, d3.event);
        }
    }
}
function init_svg () {
    $('.wrap g').remove();
    $('.wrap line').remove();
    spinner.stop();    

    var real_nodes_map = {};
    $.each(g_nodes_map, function(index, nodes){
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            real_nodes_map[node.id] = true;
        };
    })
    for (var i = 0; i < gre_ovses.length; i++) {
        var dpid = recompose_dpid(gre_ovses[i]);
        
        for (var j = 0; j < gre_ovses.length; j++) {
            var dpid2 = recompose_dpid(gre_ovses[j]);
            
            if (dpid in nodes_map && dpid2 in nodes_map) {
                var capacity = gre_ovs_capacity[j];
                if (dpid in real_nodes_map && dpid2 in real_nodes_map) {
                    g_links.push({source:nodes_map[dpid], target: nodes_map[dpid2], value:20, type:"island", capacity: capacity});
                }
            }
        };
    };

    var link = svg.selectAll("line.link").data(g_links);
    link.enter()
        .append("line").attr("class", "link")
        .on('mouseover', function(d, i) {
            highlight( d, i, this );
        })
        .style("stroke-width", function (d) { 
            var width = 1;
            if (d.type) {
                width = 3;
            }
            return width; 
        })
        .style("stroke", function (d) { 
            var color = 'black';
            
            if (d.type) {
                var rand_num = Math.random();
                var bandwidth = rand_num * parseInt(d.capacity.slice(0, d.capacity.length - 1));
                d.bandwidth = bandwidth.toFixed(2);
                if (rand_num < 0.3) {
                    color = 'red';
                } else if (rand_num < 0.6) {
                    color = 'orange';
                } else if (rand_num < 0.9) {
                    color = 'yellow';
                } else {
                    color = 'green';
                }
            }
            return color; 
        });
        //.attr('haha', function(d){ return d.source.id + " " + d.target.id})
    link.append("text").attr("dx", 20).attr("dy", ".35em")
        .text(function(d) { return "sasa"});
    link.exit().remove();
    var node = svg.selectAll(".node").data(g_nodes);
    
    node.enter().append("g")
    .attr("class", "node")
    .on('mouseup', function() {
      if(!mousedown_node) return;
        svg.call(d3.behavior.zoom().on("zoom", rescale))
        mousedown_node = null;
    })
    .on('mouseover', function(d, i) {
        highlight( d, i, this );
    })
    .on('mouseout', function(d, i) {
        tooltip.hideTooltip();
    })
    .on('mousedown', function(d) {
      if(d3.event.ctrlKey) return;
        svg.call(d3.behavior.zoom().on("zoom", function  (argument) {
            //d3.event.stopPropagation(); 
        }));
        mousedown_node = d;
    })
    .call(force.drag);
    node.exit().remove();

    /*
    var selected_switch_map = {};
    if (parent.selected_switches) {
        $.each(parent.selected_switches, function(island_id, dpids) {
            $.each(dpids, function (index2, dpid) {
                selected_switch_map[recompose_dpid(dpid)] = true;
            });
        })
    }
    */
    node.append("image")
        .attr("xlink:href", function (d) {
            var show_logical = $('#show-logical').attr('checked');
            if (d.id.indexOf('00:ff:') == 0 && !show_logical) {
                d.group = 2;
            }
            var ovs_image = STATIC_URL + 'topology/img/ovs.png?v=4';
            if (d.id.indexOf('00:ee:') == 0) {
                ovs_image = STATIC_URL + 'topology/img/ovs-red.png';
            }
            if (d.id.indexOf('00:ff:') == 0) {
                ovs_image = STATIC_URL + 'topology/img/ovs-green.png';
            }

            /*
            if (parent.selected_switches) {
                if (d.id in selected_switch_map) {
                    ovs_image = STATIC_URL + 'topology/img/ovs_green.png?v=3';
                }
            }
            */
            return d.group==1 ? ovs_image : STATIC_URL + "topology/img/host.png?v=5"
        })
        .attr("x", -32).attr("y", -32)
        .attr("width", 64).attr("height", 64);
    node.append("text").attr("dx", 40).attr("dy", ".35em")
        .text(function(d) { return d.db_name ? d.db_name : d.name });
    node.on("click", function (d) {
        // TODO we could add some functionality here
        if (parent.add_port) {
            if (d.group == 1) {

                var data = d;
                if (data.id in origin_nodes_map) {
                    var origin_data = origin_nodes_map[data.id];
                    if (!origin_data.ports) {
                        return;
                    }
                    var content = "";
                    $.each(origin_data.ports, function(index, port){
                        content +=  
                            "<label><input class='checkbox' type='checkbox' ";
                        if (port.db_id in parent.selected_ports) {
                            content += "checked ";
                        }
                        content += "value='" + port.db_id+ "'/> " + 
                            d.db_name + ":" + port.name + "(" + port.portNumber+ ")";
                        var port_pairs = {};
                        $.each(g_links_map[d.island_id], function(index, link) {
                            var port_pair_key = [port.portNumber, link.info['dst-port-name']].sort().join('');
                            if (port_pair_key in port_pairs) {
                                return;
                            }
                            if ((link.source.id == d.id) && (link.info['src-port'] == port.portNumber)) {
                                port_pairs[port_pair_key] = '';
                                content += ' <-----> ' + link.target.db_name + ":" + link.info['dst-port-name'] + "(" + link.info['dst-port'] + ")";
                            }
                            port_pair_key = [port.portNumber, link.info['src-port-name']].sort().join('');
                            if (port_pair_key in port_pairs) {
                                return;
                            }
                            if ((link.target.id == d.id) && (link.info['dst-port'] == port.portNumber)) {
                                port_pairs[port_pair_key] = '';
                                content += ' <-----> ' + link.source.db_name + ":" + link.info['src-port-name'] + "(" + link.info['src-port'] + ")";
                            }
                        });
                        content += "</label>";
                    });
                    $('.port-modal .confirm-port').unbind("click");
                    $('.port-modal .confirm-port').click(function () {
                        var inputs = $('.port-modal input');
                        $.each(inputs, function (index, input) {
                            if ($(input).attr('checked')) {
                                parent.add_port($(input).val(), false);
                            } else {
                                parent.add_port($(input).val(), true);
                            }
                        });
                    });
                    $('.port-modal .modal-body').html(content);
                    $('.port-modal').modal();
                }
            }
        }
    });
    
    force.nodes(g_nodes).links(g_links).start();
    force.on("tick", function(e) {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; }).attr('fixed', true);
        if(islands.length == 1) {
            for (var i = 0; i < islands.length; i++) {
                var island = islands[i];
                //$.post('/cache_svg/' + island.id + '/', {'svg': show_svg_code()});
            };
        }
    });
    init_count ++;

};
function show_svg_code()
{
    // Get the d3js SVG element
    var tmp  = document.getElementById("svg");
    var svg = tmp.getElementsByTagName("svg")[0];

    // Extract the data as SVG text string
    var svg_xml = (new XMLSerializer).serializeToString(svg);


    // Set the content of the <pre> element with the XML
    return svg_xml;

    //Optional: Use Google-Code-Prettifier to add colors.
}

var Island = function(urlBase, island_id) {
    this.id = island_id;
    var hackBase = urlBase;
    this.hackBase = hackBase;   
    if (direct_flowvisor_api) {
        this.hackBase = "/direct" + this.hackBase;
    }
    this.count = 2;
    this.swl = new SwitchCollection();
    this.swl.hackBase = this.hackBase;
    this.hl = new HostCollection();
    this.hl.hackBase = this.hackBase;
    this.last_swl = null;
    this.last_hl = null;

    this.update = function () {
        this.count --;
        var self = this;
        if (this.count > 0) {
            return;
        }
        this.count = 2;
        setTimeout(function () {
            self.swl.fetch();
            self.hl.fetch();
        }, 5000);
        if (self.swl.pluck('id').join("") == self.last_swl && JSON.stringify(self.hl) == self.last_hl) {
            return;
        }
        self.last_swl = self.swl.pluck('id').join('');
        self.last_hl = JSON.stringify(self.hl);
        app.topology(this);
    };

    this.fetch = function () {
        this.swl.bind('reset', this.update, this);
        this.hl.bind('reset', this.update, this);
        this.swl.fetch();
        this.hl.fetch();
    }
};
function load_topology(callback) {
    tpl.loadTemplates(['home', 'status', 'topology', 'header', 'switch', 'switch-list', 'switch-list-item', 'host', 'host-list', 'host-list-item', 'port-list', 'port-list-item', 'flow-list', 'flow-list-item'],
        callback
);

    var refresh_time = 10000;
    function random_refresh () {
        setTimeout(function  () {
            refresh_time = Math.floor(Math.random() * 10000 + 2000 );
            
            var link = svg.selectAll("line.link").style("stroke", function (d) { 
                var color = 'black';
                
                if (d.type) {
                    var rand_num = Math.random();
                    var bandwidth = rand_num * parseInt(d.capacity.slice(0, d.capacity.length - 1));
                    d.bandwidth = bandwidth.toFixed(2);
                    if (rand_num < 0.3) {
                        color = 'red';
                    } else if (rand_num < 0.6) {
                        color = 'orange';
                    } else if (rand_num < 0.9) {
                        color = 'yellow';
                    } else {
                        color = 'green';
                    }
                }
                return color; 
            });
            random_refresh();
        }, refresh_time);
    }
    random_refresh();
}
