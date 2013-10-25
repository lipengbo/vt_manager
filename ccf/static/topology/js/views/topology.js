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

window.TopologyView = Backbone.View.extend({
    initialize:function () {
        this.template = _.template(tpl.get('topology'));
        this.model.bind("change", this.render, this);
        this.hosts = this.options.hosts.models;
        this.host_links = [];
    },

    render:function (eventName) {
        $(this.el).html(this.template());

        var show_logical = $('#show-logical').attr('checked');
        
        if(this.model.nodes) {
            for (var i = 0; i < this.model.nodes.length; i++) {
                this.model.nodes[i].group = 1;
                this.model.nodes[i].id = this.model.nodes[i].name;
                this.model.nodes[i].island_id = this.model.island.id;
            }
            
            for (var i = 0; i < this.hosts.length; i++) {
                host = this.hosts[i];
                if (host.attributes['ipv4'].length > 0) {
                    host.name = host.attributes['ipv4'][0] + "\n" + host.id;
                } else {
                    host.name = host.id;
                }
                host.group = 2;
                //console.log(host);
            }
            
            if ($('#quanwang').attr('checked')) {
                var all_nodes = this.model.nodes.concat(this.hosts);
            } else {
                var all_nodes = this.model.nodes;
            }
            var all_nodes_map = [];
            
            var all_node_copy = []
            _.each(all_nodes, function(n) {
                all_node_copy.push(n);
                all_nodes_map[n.id] = n;
                nodes_map[n.id] = n;
            });
            var delete_nodes = [];
            _.each(all_node_copy, function(n) {
                /*
                if (!$('#quanwang').attr('checked')) {
                    if (n.id.indexOf('00:ff:') == 0 ) {
                        delete_nodes.push(n);
                    }
                }
                */
            });
            for (var i = 0; i < delete_nodes.length; i++) {
                all_node_copy.splice(all_node_copy.indexOf(delete_nodes[i]), 1);
            };
            all_nodes = all_node_copy;
            g_nodes = [];
            g_nodes_map[this.model.island.id] = all_nodes;
            
            $.each(g_nodes_map, function (k, v) {
                g_nodes = g_nodes.concat(v);
            })
            
            for (var i = 0; i < this.hosts.length; i++) {
                host = this.hosts[i];
                //for (var j = 0; j < host.attributes['attachmentPoint'].length; j++) {
                for (var j = 0; j < 1; j++) { // FIXME hack to ignore multiple APs
                    
                    var link = {source:all_nodes_map[host.id],
                                target:all_nodes_map[host.attributes['attachmentPoint'][j]['switchDPID']],
                                attach_point: host.attributes['attachmentPoint'][j],
                                value:10};
                    if (link.source && link.target ) {
                        if (!show_logical) {
                            if (link.target.id.indexOf('00:ff:') != 0 || link.source.id.indexOf('00:ff:') != 0) {
                                continue;
                            }
                        }
                        this.host_links.push(link);
                    } else {
                        console.log("Error: skipping link with undefined stuff!")
                    }
                }
            }
            
            
            if ($('#quanwang').attr('checked')) {
                var all_links = this.model.links.concat(this.host_links);
            } else {
                var all_links = this.model.links;
            }
            
            var all_links_copy = [];
            $.each(all_links, function (index, link) {
                all_links_copy.push(link);
            })
            var deleted_link_indexes = [];
            $.each(all_links_copy, function (index, link) {
                if (!$('#quanwang').attr('checked') && link) {
                    if ((link.target && link.target.id && link.target.id.indexOf('00:ff:') == 0) || (link.source && link.source.id && link.source.id.indexOf('00:ff:') == 0)) {
                        //deleted_link_indexes.push(link);


                    }
                }
            })
            for (var i = 0; i < deleted_link_indexes.length; i++) {
                all_links_copy.splice(all_links_copy.indexOf(deleted_link_indexes[i]), 1);
            };
            all_links = all_links_copy;
            g_links_map[this.model.island.id] = all_links;
            console.log(all_links, '----')
            console.log(g_links_map)
            
            g_links = [];
            $.each(g_links_map, function (k, v) {
                g_links = g_links.concat(v);
            })
            console.log(g_links)
            
            init_svg();
        }
        return this;
    }
});
