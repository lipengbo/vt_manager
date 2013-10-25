//验证vm名称是否是字母数字下划线
function check_vminfo(){
        name = check_vm_name('name');
        flavor = check_vm_select('flavor');
        image = check_vm_select('image');
        server = check_vm_select('server');
        return name && flavor && image && server
}

function check_vm_name(obj){
	//var obj = document.getElementById(obj);
	//var info = document.getElementById(obj+"Info"); 
        var objs = document.getElementsByName(obj);
	var infos = document.getElementsByName(obj+"Info"); 
	var reg = /^[a-zA-Z_]\w*$/;
	//alert(obj.value.length);
        var results = new Array();
        var result = true;
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                info = infos[i];
                if(obj.value.length > 0){
                        if(!reg.test(obj.value))
                        {
                                showInfo(info," * 请输入字母数字下划线的组合（不以数字开头）","red");
                                results[i] = false;
                        }
                        else
                        {
                                showInfo(info,"√","green");
                                results[i] = true;
                        }
                
                }
                else
                {
                        showInfo(info," * 该项为必填项","red");
                        results[i] = false;
                }	
        }

        for(var i=0; i < objs.length; i++)
        {
                result = result && results[i];
        }
        return result
}

//验证vm的flavor,image,server等以select形式提供的选项不能为空
function check_vm_select(obj){
	//var obj = document.getElementById(obj);
	var objs = document.getElementsByName(obj);
	//var info = document.getElementById(obj+"Info"); 
	var infos = document.getElementsByName(obj+"Info"); 
        var results = new Array();
        var result = true;
        for(var i=0; i < objs.length; i++)
        {
               obj = objs[i];
               info = infos[i];
               if(obj.selectedIndex == 0){
                       showInfo(info," * 该项为必填项","red")
                        results[i] = false;
               }
               else
               {
                       showInfo(info,"√","green");
                       results[i] = true
               }	
        }
        for(var i=0; i < objs.length; i++)
        {
                result = result && results[i]
        }
        return result
}


//获取vm form的内容并填入slice清单中
function fetch_vminfo()
{
        var objs = document.getElementsByName('name');
        name_value = get_value_from_obj('name');
        //alert('name_value')
        flavor_text = get_text_from_select('flavor');
        //alert(flavor_text)
        image_text = get_text_from_select('image');
        //alert(image_text)
        server_text = get_text_from_select('server');
        //alert(server_text)
        enable_dhcp_value = get_checked_from_checkbox('enable_dhcp');
        //alert(enable_dhcp_value)
        content = ''
        for(var i=0; i < objs.length; i++)
        {
                content = content + "<tr>"
                content = content + "<td>" + name_value[i] + "</td>"
                content = content + "<td>" + flavor_text[i] + "</td>"
                content = content + "<td>" + image_text[i] + "</td>"
                content = content + "<td>" + server_text[i] + "</td>"
                content = content + "<td>" + enable_dhcp_value[i] + "</td>"
                content = content + "</tr>"
        }
        //alert(content)
        insert_content_to_obj('id_vm_tbody',content)
}

function get_text_from_select(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                //alert(obj.selectedIndex)
                text = obj.options[obj.selectedIndex].text
                results[i] = text
        }
        return results
}

function get_value_from_select(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                value = obj.value
                results[i] = value
        }
        return results
}

function get_checked_from_checkbox(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                if(obj.checked)
                {
                        results[i] = '是'
                }
                results[i] = '否'
        }
        return results
}

function get_checked_value_from_checkbox(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                results[i] = obj.checked
        }
        return results
}

function get_value_from_obj(obj)
{
	var objs = document.getElementsByName(obj);
        //var obj = document.getElementById(obj);
        var results = new Array();
        for(var i=0; i < objs.length; i++)
        {
                obj = objs[i];
                results[i] = obj.value
        }
        return results
}

function insert_content_to_obj(obj, content)
{
        var obj = document.getElementById(obj);
        obj.innerHTML = content;
}

function insert_content_to_obj1(obj, content)
{
        var obj = document.getElementById(obj);
        obj.innerHTML = obj.innerHTML + content;
}

//逐一提交vm的创建请求
function submit_vms(sliceid)
{
        var objs = document.getElementsByName('name');
        name_value = get_value_from_obj('name');
        flavor_text = get_value_from_select('flavor');
        image_text = get_value_from_select('image');
        server_text = get_value_from_select('server');
        enable_dhcp_value = get_checked_value_from_checkbox('enable_dhcp');
        for(var i=0; i < objs.length; i++)
        {
                post_vminfo(sliceid, name_value[i], flavor_text[i], image_text[i], server_text[i], enable_dhcp_value[i])
        }
        
}

function post_vminfo(sliceid, name, flavor, image, server, enable_dhcp)
{
        url = "/plugins/vt/create/vm/"+sliceid+"/";
        $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        cache: false,
        async: false,  
        data: {
                name: name,
                flavor: flavor,
                image: image,
                server: server,
                enable_dhcp: enable_dhcp
        },
        success: function(data) {
            if(data.result==1)
            {
                //alert('Failed to operator vm!')
                alert(data.error)
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


//获取被用户选择的server
function fetch_serverinfo(){
    server_names = get_select_server_name();
    server_ids = get_select_server_id();
    content = '<option value="" selected="selected">---------</option>';
    for(var i=0; i < server_ids.length; i++)
    {
        content = content + '<option value="' + server_ids[i];
        content = content +  '">';
        content = content + server_names[i];
        content = content + '</option>';
    }
    insert_content_to_obj('id_server',content);
}

function get_select_server_name(){
    var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
    var results = new Array();
    var j =0
    for(var i=0;i<switch_port_ids_obj.length;i++){
        obj = switch_port_ids_obj[i];
        if(!obj.disabled){
            servername = obj.getAttribute("servername");
            if( servername && not_contains(results, servername))
            {
                results[j] = servername;
                j++;
            }
        }
    }      
    return results
}

function get_select_server_id(){
    var switch_port_ids_obj = document.getElementsByName("switch_port_ids");
    var results = new Array();
    var j =0
    for(var i=0;i<switch_port_ids_obj.length;i++){
        obj = switch_port_ids_obj[i];
        if(!obj.disabled){
            serverid = obj.getAttribute("serverid");
            if( serverid && not_contains(results, serverid))
            {
                results[j] = serverid;
                j++;
            }
        }
    }      
    return results
}

function not_contains(a, obj) {
    for (var i = 0; i < a.length; i++) {
        if (a[i] === obj) {
            return false;
        }
    }
    return true;
}

function create_vms(sliceid)
{
    if(check_vminfo())
    {
        submit_vms(sliceid);
        window.location.href='/plugins/vt/vm/list/' + sliceid + '/'
    }
}

function open_vnc(url)
{
    window.open(url,'','width=968,height=552')
}

function do_vm_action(url)
{
        $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
            if(data.result==1)
            {
                //alert('Failed to operator vm!')
                alert(data.error)
            }
                window.location.reload();
        }
        });
}
