//入口,定期获取slice中虚拟机状态

$(document).ready(function() {
	//alert("here");
	check_vm = $("#check_vm").text();
	if(check_vm == 1){
		//alert(2);
		slice_id = $("#slice_id").text();
		setTimeout("check_vm_status("+slice_id+")",5000);
	}
});

function check_vm_status(slice_id){
	//alert(3);
	check_url = "http://" + window.location.host + "/plugins/vt/get_vms_state/"+slice_id+"/";
	var check_vm_ids_obj = document.getElementsByName("check_vm_ids");
	var check = false;
	var status;
	var cur_vm_id;
	var str;
	//alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	vms = data.vms;
        	status = 8;
        	if(vms){
	        	for(var i=0;i<check_vm_ids_obj.length;i++){
					if(check_vm_ids_obj[i].checked){
						cur_vm_id = check_vm_ids_obj[i].value;
						for(var j=0;j<vms.length;j++){
							if(vms[j].id == cur_vm_id){
								status = vms[j].state;
								break;
							}
						}
						//alert(status);
						if(status!=8){
							if(status == 9){
								$("div#controller_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-remove\"></i>";
								$("div#controller_st"+cur_vm_id).append(str);
								
								$("span#controller_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"\" class=\"btn edit\" disabled>登录</button>"
									+ "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn edit\" disabled>启动</button>";
								$("span#controller_fc"+cur_vm_id).append(str);
								
								$("div#vm_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-remove\"></i>";
								$("div#vm_st"+cur_vm_id).append(str);
								
								$("span#vm_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"\" class=\"btn edit\" disabled>登录</button>"
									+ "<button type=\"button\" onclick=\"\" class=\"btn btn-success start_btn edit\" disabled>启动</button>";
								$("span#vm_fc"+cur_vm_id).append(str);
							}else if(status == 1){
								$("div#controller_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-ok\"></i>";
								$("div#controller_st"+cur_vm_id).append(str);
								
								$("span#controller_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn edit\">登录</button>"
									+ "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn edit\">停止</button>";
								$("span#controller_fc"+cur_vm_id).append(str);
								
								$("div#vm_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-ok\"></i>";
								$("div#vm_st"+cur_vm_id).append(str);
								
								$("span#vm_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"open_vnc('/plugins/vt/vm/vnc/"+cur_vm_id+"')\" class=\"btn edit\">登录</button>"
									+ "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/"+cur_vm_id+"/destroy')\" class=\"btn btn-danger stop_btn edit\">停止</button>";
								$("span#vm_fc"+cur_vm_id).append(str);
							}else{
								$("div#controller_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-ok\"></i>";
								$("div#controller_st"+cur_vm_id).append(str);
								
								$("span#controller_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"\" class=\"btn edit\" disabled>登录</button>"
									+ "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn edit\">启动</button>";
								$("span#controller_fc"+cur_vm_id).append(str);
								
								$("div#vm_st"+cur_vm_id).empty();
								str = "";
								str = str + "<i class=\"icon-ok\"></i>";
								$("div#vm_st"+cur_vm_id).append(str);
								
								$("span#vm_fc"+cur_vm_id).empty();
								str = "";
								str = str + "<button type=\"button\" onclick=\"\" class=\"btn edit\" disabled>登录</button>"
									+ "<button type=\"button\" onclick=\"do_vm_action('/plugins/vt/do/vm/"+cur_vm_id+"/create')\" class=\"btn btn-success start_btn edit\">启动</button>";
								$("span#vm_fc"+cur_vm_id).append(str);
							}
						}
						else{
							check = true;
						}
					}
			    } 
			}    
        	if (check){
                setTimeout("check_vm_status("+slice_id+")",5000);
            } 
        }
    });
}
