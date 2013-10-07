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

window.Host = Backbone.Model.extend({

    defaults: {
        // vlan: -1,
        lastSeen: 'never',
        ip: ' ',
        swport: ' ',
    },

    // initialize:function () {}

});

window.HostCollection = Backbone.Collection.extend({

    model:Host,

    fetch:function () {
        var self = this;
        var hackBase = this.hackBase;
        //console.log("fetching host list")
        $.ajax({
            url:hackBase + "/wm/device/",
            dataType:"json",
            success:function (data) {
                console.log("fetched  host list: " + data.length);
                console.log(data);
                // data is a list of device hashes
                var models = [];
                var show_logical = $('#show-logical').attr('checked');
                _.each(data, function(h) {
                    h.id = h.mac[0];
                    
                    if (!show_logical && h.id.indexOf('7f:ff:') != 0 ) {
                        return;
                    }
                    origin_nodes_map[h.id] = h;
                    if (h['attachmentPoint'].length > 0) {
                        h.swport = _.reduce(h['attachmentPoint'], function(memo, ap) {
                            return memo + ap.switchDPID + "-" + ap.port + " "}, "");
                        //console.log(h.swport);
                        h.lastSeen = "";//new Date(h.lastSeen).toLocaleString();
                        models.push(h);
                    }
                });
                //self.trigger('add'); // batch redraws
                self.reset(models);
            }
        });

    },

    /*
     * findByName:function (key) { // TODO: Modify service to include firstName
     * in search var url = (key == '') ? '/host/' : "/host/search/" + key;
     * console.log('findByName: ' + key); var self = this; $.ajax({ url:url,
     * dataType:"json", success:function (data) { console.log("search success: " +
     * data.length); self.reset(data); } }); }
     */

});
