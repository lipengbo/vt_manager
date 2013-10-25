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

window.Topology = Backbone.Model.extend({

    url:"/wm/topology/links/json",
    
    defaults:{
        nodes: [],
        links: [],
    },

    initialize:function (options) {
        var self = this;
        self.island = options.island;
        //console.log("fetching topology")
        var hackBase = options.hackBase;
        var swl = options.island.swl;
        //console.log(hackBase)
        
        $.ajax({
            url:hackBase + self.url,
            dataType:"json",
            success:function (data) {
                //console.log("fetched topology: " + data.length);
                // console.log(data);
                self.nodes = {};
                self.links = [];

                // step 1: build unique array of switch IDs
                /* this doesn't work if there's only one switch,
                   because there are no switch-switch links
                _.each(data, function (l) {
                    self.nodes[l['src-switch']] = true;
                    self.nodes[l['dst-switch']] = true;
                });
                // console.log(self.nodes);
                var nl = _.keys(self.nodes);
                */
                var nl = swl.pluck('id');
                var db_names = swl.pluck('db_name');

                self.nodes = _.map(nl, function (n) {return {name:n}});
                for (var i = 0; i < self.nodes.length; i++) {
                    self.nodes[i].db_name = db_names[i];
                };
                console.log(self.nodes, 'nodes', swl)
                
                // step 2: build array of links in format D3 expects
                _.each(data, function (l) {
                    self.links.push({source:self.nodes[nl.indexOf(l['src-switch'])],
                                     target:self.nodes[nl.indexOf(l['dst-switch'])],
                                     info:l,
                                     capacity: bandwidth_capacities[Math.floor(Math.random() * 4)],
                                     value:10});
                });
                self.trigger('change');
                //self.set(data);
            }
        });
    }

});
