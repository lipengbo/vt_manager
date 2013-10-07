//验证slice名称是否是字母数字下划线
function check_slice_name(obj_id,flag){
	//alert("in check_slice_form");
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	//var reg = /^([u4e00-u9fa5]|[ufe30-uffa0]|[a-zA-Z_])*$/;
	var reg = /^[a-zA-Z_]\w*$/;
	//alert(obj.value.length);
	if(obj.value.length > 0){
		if(!reg.test(obj.value)){
			//alert("in 输入");
			showInfo(info," * 请输入字母数字下划线的组合（不以数字开头）","red");
			return false;
		}
		else{
			//alert("in green");
			//alert(slice_exist);
			isslice_exist(obj.value);
			if(slice_exist){
				//alert(slice_exist);
				showInfo(info," * 该slice已经存在","red");
				return false;
			}
			else{
				showInfo(info,"√","green");
				return true;
			}
		}
	}
	else{
		showInfo(info," * 必填","red");
		return false;
	}	
}
//验证slice描述信息
function check_slice_description(obj_id,flag){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	if(obj.value.length > 0){
		showInfo(info,"√","green");
		return true;
	}
	else{
		showInfo(info," * 必填","red");
		return false;
	}
}
//验证节点的选择
function check_island_id(obj_id){
	var obj = document.getElementById(obj_id);
	var info = document.getElementById(obj_id+"Info"); 
	var island_id = obj.options[obj.selectedIndex].value;
	if(obj.value == "no"){
		showInfo(info," * 必选","red");
		return false;
	}
	else{
		showInfo(info,"√","green");
		return true;
	}
}
//验证控制器的选择
function check_slice_controller(obj_name){
	var objs = document.getElementsByName(obj_name);
	for(var i=0;i<objs.length;i++){  
		if(objs[i].checked){  
			if(objs[i].value=="default_create"){  
				return true; 
			}  
			if(objs[i].value=="user_defined"){
				controller_ip_port_obj = document.getElementById("controller_ip_port");
				controller_ip_port = controller_ip_port_obj.value.split(":")
				var info = document.getElementById("controller_ip_portInfo");
				if(controller_ip_port.length != 2){
					showInfo(info," * 格式错误(ip:port)","red");
					return false;
				}
				else{
					ret1 = check_ip(controller_ip_port[0],1);
					if(!ret1){
						return false;
					}
					else{
						ret2 = check_port(controller_ip_port[1],1);
						if (ret2){
							return true;
						}
						else{
							return false;
						}
					}
				}
	  		}  
		}   
	}
}

//验证IP地址格式
function check_ip(ip,flag){
	var info = document.getElementById("controller_ip_portInfo");
	var reg=/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;//正则表达式

	if(ip.length > 0){
		//alert(ip);
		if(reg.test(ip)){
			if( RegExp.$1<256 && RegExp.$2<256 && RegExp.$3<256 && RegExp.$4<256){
				showInfo(info,"√","green")
				return true;
			}
		}
		
		showInfo(info," * 格式错误(ip:port)","red");	
		return false;
	}
	else{
		if(flag){
			showInfo(info," * 格式错误(ip:port)","red");
			return false;
		}
		else{
			return true;
		}
	}	
}

//校验端口值
function check_port(port,flag){
	var info = document.getElementById("controller_ip_portInfo");
	var reg = /^[0-9]*$/;
	if(port.length > 0){
		if(port >= 65535 || port < 0 || !reg.test(port)){
			showInfo(info," * port在(0-65535)之间","red");
			return false;
		}
		else{
			showInfo(info,"√","green");
			return true;
		}	
	}
	else{
		if(flag){
			showInfo(info," * 格式错误(ip:port)","red");
			return false;
		}
		else{
			return true;
		}
	}
}

//校验网段分配
function check_nw_num(){
	var slice_name_obj = document.getElementById("slice_name");
	var old_nw_owner_obj = document.getElementById("old_nw_owner");
	var nw_num_obj = document.getElementById("nw_num");
	var old_nw_num_obj = document.getElementById("old_nw_num");
	var slice_nw_obj = document.getElementById("slice_nw");
	var old_slice_nw_obj = document.getElementById("old_slice_nw");
	var slice_name = slice_name_obj.value;
	var old_nw_owner = old_nw_owner_obj.value;
	var nw_num = nw_num_obj.options[nw_num_obj.selectedIndex].value;
	var old_nw_num = old_nw_num_obj.value;
	var old_slice_nw = old_slice_nw_obj.value;
	var info = document.getElementById("nw_numInfo");
	
	var ajax_ret = false;
	
	if((slice_name!=old_nw_owner) || (nw_num!=old_nw_num)){
		if(old_slice_nw==''){
			check_url = "http://" + window.location.host + "/slice/create_nw/"+slice_name+"/";
		}
		else{
			if(nw_num!=old_nw_num){
				check_url = "http://" + window.location.host + "/slice/change_nw/"+old_nw_owner+"/"+slice_name+"/";
			}
			else{
				check_url = "http://" + window.location.host + "/slice/change_nw_owner/"+old_slice_nw+"/"+slice_name+"/";
			}
		}
	    $.ajax({
	        type: "GET",
	        url: check_url,
	        dataType: "json",
	        cache: false,
	        async: false,  
	        success: function(data) {
	        	//alert(data.value);
	        	if (data.value == 0){
	        		//alert(1);
	        		showInfo(info," * 分配网段失败！(改slice名称)","red");
	        		ajax_ret = false;
	            }
	            else{
	            	alert(2);
	            	if (data.value != 1){
	            		//alert(3);
	        			slice_nw_obj.innerHTML = data.value;
		             	old_slice_nw_obj.value = data.value;
	            	}
	            	old_nw_owner_obj.value = slice_name;
	    			old_nw_num_obj.value = nw_num;
	    			showInfo(info,"√","green");
	    			//alert(5);
	    			ajax_ret = true;
	            }
	        },
	        error: function(data) {
	        	showInfo(info," * 分配网段失败！(改slice名称)","red");
	    		ajax_ret = false;
	        }
	    });
	    if(ajax_ret){
	    	return true;
	    }
	    else{
	    	return false;
	    }
	}
	else{
		//alert(4);
		showInfo(info,"√","green");
		return true;
	}
}

//验证交换机端口的选择
function check_switch_port(){
	var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
	var info = document.getElementById("switch_portInfo");
	for(var i=0;i<switch_port_ids_obj.length;i++){
		if(switch_port_ids_obj[i].checked){
			//alert(switch_port_ids_obj[i].value);
			switch_port_id = switch_port_ids_obj[i].value;
			switchtype_obj = document.getElementById("switchtype"+switch_port_id);
			if(switchtype_obj.value == 3){
				showInfo(info,"","green");
				return true;
			}
		}
    }
    showInfo(info," * 必选一台虚拟机关联节点！","red");
	return false;
}

var slice_exist;
//校验所填的slice是否存在
function isslice_exist(slicename){
	//alert (slicename)
	check_url = "http://" + window.location.host + "/slice/check_slice_name/"+slicename+"/";
	//alert(check_url)
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	if (data.value == 1)
             {
                //alert("in true")
                slice_exist = true;
             } 
             else
             {
              	//alert("in false");
                slice_exist = false;
             }
        }
    });
}


//显示信息
function showInfo(_info,msg,color){
    var info=_info;
    info.innerHTML = msg;
    info.style.color=color;
}