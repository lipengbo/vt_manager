//当前画布的宽，高，左边距，上边距，图标（交换机和主机）的宽，高
var mbWidth;
var mbHeight;
var mbLeft;
var mbTop;
var pic_width;
var pic_height;

//用于存储拓扑信息的数据结构
var switches;	// (DPIP, x, y)
var hosts;	// (MAC, DPIP, x1, y1, x2, y2, status)
var links;	// (src_dpid, des_dpid, x1, y1, x2, y2)
var hosts_special;	// (MAC, x1, y1, drawed, status)
var host_links;	// (MAC, NUM, LEVEL, DPID1, ...)
var host_vss;	// (MAC, DPIP, x1, y1, x2, y2)

//当前树根节点（交换机）
var rootIndex;
var rootSw;

//总体，纵向，横向缩放比例，每层高度，当前树的层数
var sf;
var ysf;
var xsf;
var levelHeight;
var levelNum;

//每层交换机个数，主机个数，已确定坐标的交换机个数，主机个数，交换机宽度，主机宽度
var levelNodesNum;
var levelHostsNum;
var levelUsedNodesNum;
var levelUsedHostsNum;
var levelNodesWidth;
var levelHostsWidth;
var swHostNum;//交换机下挂主机个数，预留

//标记交换机与交换机的连线是否被用
var linksSign;
//标记交换机是否被遍历到
var sw_in_circle;
//标记交换机与交换机的连线是否被遍历到
var link_in_circle;

//树个数，树层数，树最大宽度（每层节点个数），树根节点索引，当前树最大宽度，树最大层数，森林总宽度
var treeNum;
var treeLevels;
var treeLevelNodes;
var treeRootIndexs;
var currMaxLevelNodes;
var maxTreeLevels;
var totalLevelNodes;

//原始画布宽度，高度，原始图标宽度，高度
var rs_mbWidth;
var rs_mbHeight;
var rs_pic_width;
var rs_pic_height;

//拓扑类型，0为首页拓扑，根据slice个数决定拓扑个数，1为slice编辑页面拓扑，只显示一个
var topology_type;


//设置交换机下挂主机个数
function setSwHostNum(){
	for(var i = 0; i < switches.length; i++){
		for(var j = 0; j < hosts.length; j++){
			if(hosts[j][1] == switches[i][0]){
				swHostNum[i]++;
			}
		}
	}
}

function getSwitchIndex(Dpip){
	for(var i=0;i<switches.length;i++){
		if(switches[i][0]==Dpip){
			return i;
		}	
	}
}

//判断是否有重叠的连线
function isBlocked(i){
	var srcDpid = links[i][0];
	var dstDpid = links[i][1];
	var srcIndex = getSwitchIndex(srcDpid);
	var dstIndex = getSwitchIndex(dstDpid);
	
	var x1 = links[i][2]-pic_width/2, y1 = links[i][3]-pic_height/2;
	var x2 = links[i][4]-pic_width/2, y2 = links[i][5]-pic_height/2;
	
	for(var i=0;i<switches.length;i++){
		if(i != srcIndex && i != dstIndex){
			if(x1 == x2){
				if(switches[i][1] == x1 && 
				 ( (switches[i][0] > y1 && switches[i][0] < y2) || (switches[i][0] < y1 && switches[i][0] > y2) ) ) {
					return true; 
				}
			}
			if(y1 == y2){
				if(switches[i][2] == y1 && 
					( (switches[i][1] > x1 && switches[i][1] < x2) || (switches[i][1] < x1 && switches[i][1] > x2) ) ){
					return true; 
				}
			}
		}	
	}
	return false;				
	//switchUsedNum[key] = 0;
}

//根据坐标画slice拓扑
function drawTopology(slicec){
	if(slicec == -1){
		$("div#content").empty();
	}
	else{
		$("div#content"+slicec).empty();
		//if(slicec == 0){
		//	$("div#content1").empty();
		//}else if(slicec == 1){
		//	$("div#content2").empty();
		//}else if(slicec == 2){
		//	$("div#content3").empty();
		//}else if(slicec == 3){
		//	$("div#content4").empty();
		//}
	}
	var static_url = $("#STATIC_URL").text();	
	var str = "";
	//if(slicec > -1){
	//	str = str + "<a href=\"/slice_detail/" + slice_id + "/1/\">";
	//}	
	str = str + "<svg id='svgc' width='100%' height='100%' version='1.1' xmlns='http://www.w3.org/2000/svg'>"
		
	for(var i = 0; i < links.length; i++){
		if(link_in_circle[i] == 1){
			str = str + "<g class='node' transform='translate(10,10)'>"
				+ "<line x1='" + links[i][2] + "' y1='" + links[i][3] + ""
				+"' x2='" + links[i][4] + "' y2='" + links[i][5] + "' style='stroke:black;stroke_width:3'></line> "
				+ "</g> ";
		}else{
			if( isBlocked(i) ){ 
				var x1 = links[i][2], y1 = links[i][3], x2 = links[i][4], y2 = links[i][5];
				var x12 = (x2+x1)/2, y12 = ((y1 + y2)/2);
				if(y1 == y2){
					y12 = y1 + pic_height*(0.5 + 0.2);
				}
				if(x1 == x2){
					x12 = x1 + pic_width*(0.5 + 0.1);
				}
				str = str + "<g class='node' transform='translate(10,10)'>"
					+ "<line x1='" + x1 + "' y1='" + y1 + "" 
					+ "' x2='" + x12 + "' y2='" + y12 + "'"
					+ "style='stroke:black;stroke_width:3'/>"
					+ "<line x1='" + x12 + "' y1='" + y12 + ""
					+ "' x2='" + x2 + "' y2='" + y2 + "'"
					+ "style='stroke:black;stroke_width:3'/>"
					+ "</g> ";
			}else{
				str = str + "<g class='node' transform='translate(10,10)'>"
					+ "<line x1='" + links[i][2] + "' y1='" + links[i][3] + "" 
					+ "' x2='" + links[i][4] + "' y2='" + links[i][5] + "' style='stroke:black;stroke_width:3'></line> "
					+ "</g> ";
			}			
		}
	
	}
	
	
	for(var i = 0; i < switches.length; i++){
		str = str + "<g class='node' transform='translate(10,10)'>"
				+ "<image xlink:href='" + static_url + "img/switch.png' x='" + switches[i][1] + "' y='" + switches[i][2] + "" +
						"' width='" + pic_width + "' height='" + pic_height + "'></image>"
				+ "<title>" + switches[i][0] + "</title>"
			+ "</g> ";
	}
	
	for(var i = 0; i < host_vss.length; i++){
		str = str + "<g class='node' transform='translate(10,10)'>"
				+ "<line x1='" + host_vss[i][2] + "' y1='" + host_vss[i][3] + "" +
						"' x2='" + host_vss[i][4] + "' y2='" + host_vss[i][5] + "' style='stroke:rgb(99,99,99);stroke_width:2'></line> "
			+ "</g> ";
	}

	for(var i = 0; i < hosts.length; i++){
		str = str + "<g class='node' transform='translate(10,10)'>";
		if (hosts[i][6] == 0){
			str = str + "<image xlink:href='" + static_url + "img/host_down.png' x='" + hosts[i][2] + "' y='" + hosts[i][3] + "" +
					"' width='" + pic_width + "' height='" + pic_height + "'></image>";
		}
		else{
			str = str + "<image xlink:href='" + static_url + "img/host.png' x='" + hosts[i][2] + "' y='" + hosts[i][3] + "" +
					"' width='" + pic_width + "' height='" + pic_height + "'></image>";
		}
		str = str+ "<title>ip:" + hosts[i][0] + "</title>  "
			+ "<line x1='" + hosts[i][4] + "' y1='" + hosts[i][5] + "" +
					"' x2='" + (hosts[i][2] + (pic_width*0.5)) + "' y2='" + hosts[i][3] + "' style='stroke:rgb(99,99,99);stroke_width:2'></line> "
			+ "</g> ";
	}
	
	for(var i = 0; i < hosts_special.length; i++){
		str = str + "<g class='node' transform='translate(10,10)'>";
		if (hosts_special[i][4] == 0){
			str = str + "<image xlink:href='" + static_url + "img/host_down.png' x='" + hosts_special[i][1] + "' y='" + hosts_special[i][2] + "" +
						"' width='" + pic_width + "' height='" + pic_height + "'></image>";
		}
		else{
			str = str + "<image xlink:href='" + static_url + "img/host.png' x='" + hosts_special[i][1] + "' y='" + hosts_special[i][2] + "" +
						"' width='" + pic_width + "' height='" + pic_height + "'></image>";
		}
		str = str+ "<title>ip:" + hosts_special[i][0] + "</title>  "
			+ "</g> ";
	}
	
	str = str + "</svg>";
	//if(slicec > -1){
	//	str = str + "</a>";
	//}
		
	//$("div#content").append(str);	
	if(slicec == -1){
		$("div#content").append(str);
	}
	else{
		$("div#content"+slicec).append(str);
		//if(slicec == 0){
		//	$("div#content1").append(str);
		//}else if(slicec == 1){
		//	$("div#content2").append(str);
		//}else if(slicec == 2){
		//	$("div#content3").append(str);
		//}else if(slicec == 3){
		//	$("div#content4").append(str);
		//}
	}
	
}

//设置根节点坐标
function setRootSwitchxy(){
	switches[rootIndex][1] = mbLeft + (mbWidth) / 2.0; 
	switches[rootIndex][2] = levelHeight * 0.1;  
}

//广度优先遍历交换机，确定交换机坐标及下挂的主机坐标
function drawSwitch(fatherObj, level){
	if(fatherObj == null){
		return level;
	}
	
	var childSw = new Array();
	var cnum = 0;
	for(var i = 0; i < links.length; i++){
		if(linksSign[i] != 1 && links[i][0] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][1];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}else if(linksSign[i] != 1 && links[i][1] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][0];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}
	}
	
	//确定该交换机下接多个交换机的主机的坐标
	for(var k = 0; k < host_links.length; k++){
		if(host_links[k][2] == level && hosts_special[k][1]==0 && hosts_special[k][2]==0){
			for(var j = 0; j < host_links[k][1]; j++){
				if(host_links[k][j+3] == fatherObj[0]){
					hosts_special[k][1] = mbLeft + levelHostsWidth[level] * (levelUsedHostsNum[level] + 0.6);
					levelUsedHostsNum[level]++;
					hosts_special[k][2] = levelHeight * (level+0.6);
				}
			}
		}
	}
	
	//确定该交换机下接一个交换机的主机的坐标
	for(var j = 0; j < hosts.length; j++){
		if(hosts[j][1] == fatherObj[0]){
			hosts[j][2] = mbLeft + levelHostsWidth[level] * (levelUsedHostsNum[level] + 0.51);
			levelUsedHostsNum[level]++;
			hosts[j][3] = levelHeight * (level+0.6);
		}
	}
	
	//确定该交换机的坐标
	for(var i = 0; i < childSw.length; i++){
		childSw[i][1] = mbLeft + levelNodesWidth[level] * (levelUsedNodesNum[level] + 0.5);
		levelUsedNodesNum[level]++;
		childSw[i][2] = levelHeight * (level+1); 
		drawSwitch(childSw[i], level+1);
	}
}

//确定交换机与交换机的连线的坐标
function drawLine(){ 
	for(var i = 0; i < links.length; i++){
			var dpidSrc = links[i][0];
			var dpidDst = links[i][1];
			var swSrc = getSwitch(dpidSrc);
			var swDst = getSwitch(dpidDst);
			links[i][2] = swSrc[1] + pic_width/2;
			links[i][3] = swSrc[2] + pic_height/2;
			links[i][4] = swDst[1] + pic_width/2;
			links[i][5] = swDst[2] + pic_height/2;
	}
}

// 确定连接一个交换机的主机的目标交换机坐标
function drawHost(){
    for(var i=0;i<switches.length;i++){ //遍历得某交换机下挂有多少主机
		for(var j=0;j<hosts.length;j++){
			if(hosts[j][1] == switches[i][0]){
				hosts[j][4] = switches[i][1] + (pic_width / 2);
				hosts[j][5] = switches[i][2] + pic_height;
			}
		}
		
    }
}


// 确定所有与多个交换机相连的主机的连线的坐标
function drawHostVss(){
	var num;
	var j=0;
	for(i=0;i<switches.length;i++){
		for(var k = 0; k < host_links.length; k++){
			num = host_links[k][1];
			for(var l = 0; l < num; l++){
				if(host_links[k][l+3] == switches[i][0]){
					host_vss[j] = new Array(host_links[k][0], switches[i][0], 0, 0, 0, 0);
					host_vss[j][2] = hosts_special[k][1] + (pic_width / 2);
					host_vss[j][3] = hosts_special[k][2] + (pic_height / 2);
					host_vss[j][4] = switches[i][1] + (pic_width / 2);
					host_vss[j][5] = switches[i][2] + pic_height;
					j++;			
				}
			}
		}
	}
}

//设置树中各元素坐标
function setLocation(){
	//计算树中每层的主机个数，交换机个数
	for(var i = 0; i <= levelNum; i++){
		levelNodesNum[i] = 0;
		levelHostsNum[i] = 0;
	}
	for(var k = 0; k < host_links.length; k++){
		if(host_links[k][2] != -1){
			hosts_special[k][3] = 1;
		}
		host_links[k][2] = -1;
	}
	initLevelNodesNum(rootSw, 0);
	resetLinksSign();
	
	//计算树中每层的主机所占宽度，交换机所占宽度
	for(var i = 0; i <= levelNum; i++){	
		if(levelNodesNum[i] == 0){
			levelNodesWidth[i] = mbWidth / 1;
		}else{
			levelNodesWidth[i] = mbWidth / levelNodesNum[i];
		}
		if(levelHostsNum[i] == 0){
			levelHostsWidth[i] = mbWidth / 1;
		}else{
			levelHostsWidth[i] = mbWidth / levelHostsNum[i];
		}
		levelUsedNodesNum[i] = 0;	
		levelUsedHostsNum[i] = 0;	
	}
	
	//设置根节点坐标
	setRootSwitchxy();
	//设置交换机与下挂主机坐标
	drawSwitch(rootSw, 0);
	resetLinksSign();
	//设置交换机与交换机连线坐标
	drawLine();
	//设置连一个交换机的主机的目的交换机坐标
	drawHost();
	//设置连多个交换机的主机的连线坐标
	drawHostVss();
}

//根据sw_in_circle判断交换机是否被遍历过
function isSwUsed(sw){
	for(var i = 0; i < switches.length; i++){
		if(switches[i][0] == sw[0] && sw_in_circle[i] == 1){
			return true;
		}
	}
	return false;
}

//根据dpid查找交换机
function getSwitch(Dpip){
	for(var i=0;i<switches.length;i++){
		if(switches[i][0]==Dpip){
			return switches[i];
		}	
	}
}

//标记遍历到的交换机
function setCircleSign(sw){
	for(var i = 0; i < switches.length; i++){
		if(switches[i][0] == sw[0]){
			sw_in_circle[i] = 1;			
			break;
		}
	}
}

//广度优先遍历交换机，破环
function findCircle(fatherObj){
	if(fatherObj == null){
		return;
	}
	setCircleSign(fatherObj);
	
	var childSw = new Array();
	var cnum = 0;
	for(var i = 0; i < links.length; i++){
		if(links[i][0] == fatherObj[0]){
			var DestDpip = links[i][1];
			var destSwitch = getSwitch(DestDpip);
			if(!isSwUsed(destSwitch)){
				setCircleSign(destSwitch);
				link_in_circle[i] = 1;
				childSw[cnum] = destSwitch;
				cnum++;
			}
		}else if(links[i][1] == fatherObj[0]){
			var DestDpip = links[i][0];
			var destSwitch = getSwitch(DestDpip);
			if(!isSwUsed(destSwitch)){
				setCircleSign(destSwitch);
				link_in_circle[i] = 1;
				childSw[cnum] = destSwitch;
				cnum++;
			}
		}
	}
	for(var i = 0; i < childSw.length; i++){
		findCircle(childSw[i]);
	}

}

//重置linksSign
function resetLinksSign(){
	for(var i = 0; i < links.length; i++){
		if(link_in_circle[i] == 0){
			linksSign[i] = 1;
		}else{
			linksSign[i] = -1;
		}
	}

}

//获取树的层数	
function getLevelNum(fatherObj,level){
	if(fatherObj == null){
		return level;
	}
	
	if(level > levelNum){
		levelNum = level;
	}
	
	var childSw = new Array();
	var cnum = 0;
	for(var i = 0; i < links.length; i++){
		if(linksSign[i] != 1 && links[i][0] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][1];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}else if(linksSign[i] != 1 && links[i][1] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][0];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}
	}
	
	for(var i = 0; i < childSw.length; i++){
		getLevelNum(childSw[i], level+1);
	}		
}

//获取树的宽度
function initLevelNodesNum(fatherObj, level){
	if(fatherObj == null){
		return level;
	}
	
	var childSw = new Array();
	var cnum = 0;
	var HostNum = 0;
	for(var i = 0; i < links.length; i++){
		if(linksSign[i] != 1 && links[i][0] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][1];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}else if(linksSign[i] != 1 && links[i][1] == fatherObj[0]){
			linksSign[i] = 1;
			var DestDpip = links[i][0];
			childSw[cnum] = getSwitch(DestDpip);
			cnum++;
		}
	}
	
	for(var j = 0; j < hosts.length; j++){
		if(hosts[j][1] == fatherObj[0]){
			HostNum++;
		}
	}
	var num;
	var level_pre;
	
	for(var k = 0; k < host_links.length; k++){
		if(hosts_special[k][3] == 0){
			num = host_links[k][1];
			for(var l = 0; l < num; l++){
				if(host_links[k][l+3] == fatherObj[0]){
					if(host_links[k][2] < level){
						HostNum++;
						level_pre = host_links[k][2];
						levelHostsNum[level_pre] = levelHostsNum[level_pre] - 1;
						host_links[k][2] = level;
					}				
				}
			}
		}
	}
	
	levelNodesNum[level] = levelNodesNum[level] + cnum;	
	if(currMaxLevelNodes < levelNodesNum[level]){
		currMaxLevelNodes = levelNodesNum[level];
	}
	
	levelHostsNum[level] = levelHostsNum[level] + HostNum;
	if(currMaxLevelNodes < levelHostsNum[level]){
		currMaxLevelNodes = levelHostsNum[level];
	}
	
	for(var i = 0; i < childSw.length; i++){
		initLevelNodesNum(childSw[i], level+1);
	}
}

//确定当前树的画布位置
function checkBoard(treei){	
	mbWidth = rs_mbWidth * treeLevelNodes[treei]/totalLevelNodes;
	var forwardTreeNodes = 0;
	for(var i=0; i<treei; i++){
		forwardTreeNodes = forwardTreeNodes + treeLevelNodes[i];
	}
	mbLeft = rs_mbWidth * forwardTreeNodes/totalLevelNodes;
	mbTop = 0 * sf;
	
    pic_width = rs_pic_width * sf;
    pic_height = rs_pic_height * sf;
    levelHeight = pic_height * 3;
}


//根据根索引设置根交换机rootSw
function setRootSwitch(){
	if(rootIndex >= switches.length || rootIndex < 0){
		rootIndex = 0;
	} 
	rootSw = switches[rootIndex];
}

//str类型转化为json数据
function strToJson(str){ 
    var json = (new Function("return " + str))(); 
    return json; 
}

//全局变量，拓扑数据信息初始化，采用ajax获取数据库数据
function init(){
	switches = null;
	hosts = null;
	links = null;	
	rootIndex = 0;
	levelNum = 0;
	ysf = 1;
	xsf = 1;
	sf = 1;	
	levelNodesNum = null;
	levelHostsNum = null;
	levelUsedNodesNum = null;
	levelUsedHostsNum = null;
	levelNodesWidth = null;
	levelHostsWidth = null;
	swHostNum = null;	
	linksSign = null;	
	sw_in_circle = null;
	link_in_circle = null;
	treeNum = 0;
	treeLevels = null;
	treeLevelNodes = null;
	treeRootIndexs = null;
	currMaxLevelNodes = 0;
	maxTreeLevels = 0;
	totalLevelNodes = 0;
	hosts_special = null;
	host_links = null;
	host_vss = null;

	switches = new Array();
	hosts = new Array();
	links = new Array();	
	levelNodesNum = new Array();
	levelHostsNum = new Array();
	levelUsedNodesNum = new Array();
	levelUsedHostsNum = new Array();
	levelNodesWidth = new Array();
	levelHostsWidth = new Array();
	swHostNum = new Array();	
	linksSign = new Array();	
	sw_in_circle = new Array();
	link_in_circle = new Array();
	treeLevels = new Array();
	treeLevelNodes = new Array();
	treeRootIndexs = new Array();
	hosts_special = new Array();
	host_links = new Array();
	host_vss = new Array();
	
	var tempLinks = new Array();
	var srcLinks = new Array();
	var sign = new Array();
	//获取数据库中该slice的拓扑信息	
	var topology_url = "http://" + window.location.host + "/slice/topology/"+slice_id+"/";
	$.ajaxSetup({  
	    async : false  
	}); 
	$.get(topology_url, function(responseTxt,statusTxt,xhr){
		if(statusTxt=="success")
		{
			responseTxt=strToJson(responseTxt);
			switches = responseTxt.switches;
			srcLinks = responseTxt.links;
			normals = responseTxt.normals;
			specials = responseTxt.specials;
			//获取数据库中该slice的交换机信息
			for(var key=0; key< switches.length; key++){
				switches[key] = new Array(switches[key].dpid, 0, 0);
			}
			//获取数据库中该slice的交换机的连接信息
			for(var key=0; key< srcLinks.length; key++){
				tempLinks[key] = new Array(srcLinks[key].src_switch, srcLinks[key].dst_switch, 0, 0, 0 ,0);
				sign[key] = 0;
			}
			// 初始化links数组，使其连接无重复
			for(var i = 0; i < tempLinks.length - 1; i++){
				if(sign[i] == 0){
					for(var j = i+1; j < tempLinks.length; j++){
						if(tempLinks[i][0] == tempLinks[j][1] && tempLinks[i][1] == tempLinks[j][0]){
							sign[j] = 1;
						}
					}
				}
			}
			
			var linksIndex = 0;
			for(var i = 0; i < sign.length; i++){
				if(sign[i] == 0){
					links[linksIndex] = tempLinks[i];
					linksIndex++;
				}
			}
			//获取数据库中该slice的主机信息
			for(var key1=0; key1< normals.length; key1++){
				hosts[key1] = new Array(normals[key1].macAddress, normals[key1].switchDPID, 0, 0, 0, 0, normals[key1].hostStatus);
			}
			var special_index = -1;
			var k=0;
			for(var key2=0; key2< specials.length; key2++){
				if(key2!=0 && specials[key2].hostid==specials[key2-1].hostid){
					host_links[special_index][1] = host_links[special_index][1] + 1;
					k = host_links[special_index][1];
					host_links[special_index][k + 2] = specials[key2].switchDPID;
				}
				else{
					special_index++;
					hosts_special[special_index] = new Array(specials[key2].macAddress,0,0,0,specials[key2].hostStatus);
					host_links[special_index] = new Array();
					host_links[special_index][0] = specials[key2].hostid;
					host_links[special_index][1] = 1;
					host_links[special_index][2] = -1;
					host_links[special_index][3] = specials[key2].switchDPID;
				}
			}
			
		}
		else if(statusTxt=="error")
		{
			alert("Error switch: "+xhr.status+": "+xhr.statusText);
		}
	})
	.success(function(){	})
	.error(function(){		})
	.complete(function(){	});
	
	for(var i = 0; i < switches.length; i++){
		sw_in_circle[i] = 0;
		swHostNum[i] = 0;
	}
	
	setRootSwitch();
	
	for(var i = 0; i < links.length; i++){
		linksSign[i] = -1;
		link_in_circle[i] = 0;
	}
}

//静态初始化拓扑数据，用于测试
function initCircleTemp(){
	switches = null;
	hosts = null;
	links = null;
	rootIndex = 0;
	levelNum = 0;
	ysf = 1;
	xsf = 1;
	sf = 1;	
	levelNodesNum = null;
	levelHostsNum = null;
	levelUsedNodesNum = null;
	levelUsedHostsNum = null;
	levelNodesWidth = null;
	levelHostsWidth = null;
	swHostNum = null;	
	linksSign = null;	
	sw_in_circle = null;
	link_in_circle = null;
	treeNum = 0;
	treeLevels = null;
	treeLevelNodes = null;
	treeRootIndexs = null;
	currMaxLevelNodes = 0;
	maxTreeLevels = 0;
	totalLevelNodes = 0;
	hosts_special = null;
	host_links = null;
	host_vss = null;

	switches = new Array();
	hosts = new Array();
	links = new Array();
	levelNodesNum = new Array();
	levelHostsNum = new Array();
	levelUsedNodesNum = new Array();
	levelUsedHostsNum = new Array();
	levelNodesWidth = new Array();
	levelHostsWidth = new Array();
	swHostNum = new Array();	
	linksSign = new Array();	
	sw_in_circle = new Array();
	link_in_circle = new Array();
	treeLevels = new Array();
	treeLevelNodes = new Array();
	treeRootIndexs = new Array();
	hosts_special = new Array();
	host_links = new Array();
	host_vss = new Array();
		
	switches[0] = new Array("00:01", 0, 0);			switches[1] = new Array("00:02", 0, 0);
	switches[2] = new Array("00:03", 0, 0);			switches[3] = new Array("00:04", 0, 0);
	switches[4] = new Array("00:05", 0, 0);			switches[5] = new Array("00:06", 0, 0);
	switches[6] = new Array("00:07", 0, 0);			switches[7] = new Array("00:08", 0, 0);
	switches[8] = new Array("00:09", 0, 0);			switches[9] = new Array("00:10", 0, 0);
	switches[10] = new Array("00:11", 0, 0);		
	
	switches[11] = new Array("00:13", 0, 0);		switches[12] = new Array("00:14", 0, 0);
	switches[13] = new Array("00:15", 0, 0);		switches[14] = new Array("00:16", 0, 0);

	switches[15] = new Array("00:17", 0, 0);
	
	for(var i = 0; i < switches.length; i++){
		sw_in_circle[i] = 0;
		swHostNum[i] = 0;
	}
	
	setRootSwitch();

	links[0] = new Array("00:01", "00:03", 0, 0, 0, 0);
	links[1] = new Array("00:02", "00:03", 0, 0, 0, 0);
	links[2] = new Array("00:04", "00:06", 0, 0, 0, 0);
	links[3] = new Array("00:05", "00:06", 0, 0, 0, 0);
	links[4] = new Array("00:03", "00:06", 0, 0, 0, 0);
	links[5] = new Array("00:03", "00:07", 0, 0, 0, 0);
	links[6] = new Array("00:06", "00:08", 0, 0, 0, 0);
	links[7] = new Array("00:08", "00:09", 0, 0, 0, 0);
	links[8] = new Array("00:08", "00:10", 0, 0, 0, 0);
	links[9] = new Array("00:10", "00:11", 0, 0, 0, 0);	
	links[10] = new Array("00:07", "00:08", 0, 0, 0, 0);
	
	links[11] = new Array("00:13", "00:14", 0, 0, 0, 0);
	links[12] = new Array("00:13", "00:15", 0, 0, 0, 0);
	links[13] = new Array("00:13", "00:16", 0, 0, 0, 0);
	links[14] = new Array("00:14", "00:15", 0, 0, 0, 0);
	links[15] = new Array("00:14", "00:16", 0, 0, 0, 0);
	links[16] = new Array("00:15", "00:16", 0, 0, 0, 0);
	
	
	for(var i = 0; i < links.length; i++){
		linksSign[i] = -1;
		link_in_circle[i] = 0;
	}
	
	hosts[0] = new Array("01","00:01",0, 0, 0, 0, 0)
	hosts[1] = new Array("02","00:01",0, 0, 0, 0, 1)
	hosts[2] = new Array("03","00:01",0, 0, 0, 0, 1)
	hosts[3] = new Array("04","00:01",0, 0, 0, 0, 0)
	
	hosts[4] = new Array("05","00:03",0, 0, 0, 0, 0)
	hosts[5] = new Array("06","00:05",0, 0, 0, 0, 1)
	hosts[6] = new Array("07","00:05",0, 0, 0, 0, 0)
	hosts[7] = new Array("10","00:05",0, 0, 0, 0, 1)
	hosts[8] = new Array("10","00:09",0, 0, 0, 0, 0)
	
	hosts[9] = new Array("10","00:13",0, 0, 0, 0, 1)
	hosts[10] = new Array("10","00:14",0, 0, 0, 0, 0)
	hosts[11] = new Array("10","00:14",0, 0, 0, 0, 0)
	hosts[12] = new Array("10","00:16",0, 0, 0, 0, 0)
	
	//hosts_special[0] = new Array("08", 0, 0, 0, 1)
	//host_links[0] = new Array("08", 2, -1, "00:01", "00:02")
	//hosts_special[1] = new Array("09", 0, 0, 0, 0)
	//host_links[0] = new Array("08", 4, -1, "00:01", "00:05", "00:03", "00:09")
	//host_links[1] = new Array("09", 3, -1, "00:11", "00:08", "00:13")
}

//初始化画布，图标
function initCheckBoard(conti){
	if(conti == -1){
		rs_mbWidth = 980* 0.9;
		rs_mbHeight = 300;
		rs_pic_width = 50;
		rs_pic_height = 30;
	}
	else{
		rs_mbWidth = 480 * 0.9;
		rs_mbHeight = 220;
		rs_pic_width = 50;
		rs_pic_height = 30;
	}
	mbWidth = rs_mbWidth;
	mbHeight = rs_mbHeight;
	mbLeft = 0;
	mbTop = 0;
	
    pic_width = rs_pic_width;
    pic_height = rs_pic_height;
    levelHeight = pic_height * 3;
}


var getDegrees = function(edges) {
    "use strict";
    var degree = {}, node = 0;
    for (var i in edges){
        for (var j in [0, 1]) {
            node = edges[i][j];
            if (!degree[node]) {
                degree[node] = 1;
            } else {
                degree[node] = degree[node] + 1;
            }
        }
    }
    return degree;
}

function maxDegree (degrees){
    var maxDegree = -1, max_idx = -1;
    for (var i in switches){
        if (sw_in_circle[i] != 1){
            dg = degrees[switches[i][0]] || 0;
            if (dg > maxDegree) {
                maxDegree = dg;
                max_idx = i;
            }
        }
    }
    return max_idx;
}

//画一个slice的拓扑，参数conti表示对应的html页面中的div编号（-1对应slice编辑页面中的div）
function draw(conti){
	if(conti != -1){
		slice_id = conti;
	}
	initCheckBoard(conti);	
	init();
	//initCircleTemp();
	
	//确定slice中有几棵树，每棵树的层数，宽度
	var degrees = getDegrees(links)
	for(var s=0; s<switches.length; s++){
		currMaxLevelNodes = 1;
		levelNum = 0;
		
		//设置树的根节点
        i = maxDegree(degrees);
        if(i == -1){
        	break;
        }
		treeRootIndexs[treeNum] = i;
		rootIndex = i;
		setRootSwitch();
		
		//从根节点开始遍历交换机（广度优先遍历，破环)
		findCircle(rootSw);
		resetLinksSign();
		
		//获取树的层数	
		getLevelNum(rootSw,0);
		resetLinksSign();
		if(maxTreeLevels <levelNum){
			maxTreeLevels = levelNum;
		}
		treeLevels[treeNum]=levelNum;
		
		//获取树的宽度
		levelNodesNum = null;
		levelHostsNum = null;
		levelNodesNum = new Array(0);
		levelHostsNum = new Array(0);
		for(var j=0; j<=levelNum; j++){
			levelNodesNum[j] = 0;
			levelHostsNum[j] = 0;
		}
		//一个主机连接不同树的多个交换机时，主机放在第一棵树上
		for(var k = 0; k < host_links.length; k++){
			if(host_links[k][2] != -1){
				hosts_special[k][3] = 1;
			}
			host_links[k][2] = -1;
		}
		initLevelNodesNum(rootSw, 0);
		resetLinksSign();
		treeLevelNodes[treeNum]=currMaxLevelNodes;
		
		totalLevelNodes = totalLevelNodes + currMaxLevelNodes;
		treeNum++;
		currMaxLevelNodes = 0;
	}

	if(totalLevelNodes == 0){
		return;
	}
	
	//根据树的最大层数确定缩放比例
	if(maxTreeLevels > 2){
		ysf = mbHeight/(mbHeight + levelHeight * (maxTreeLevels-2));
	}
	sf = ysf;

	for(var k=0; k<hosts_special.length; k++){
		hosts_special[k][3] = 0;
		host_links[k][2] = -1;
	}
	//确定slice中的树的各元素坐标
	for(var i=0; i<treeNum; i++){
		rootIndex = treeRootIndexs[i];
		setRootSwitch();
		levelNum = treeLevels[i];
		//确定当前树的画布位置
		checkBoard(i);
		//确定树中各元素坐标
		setLocation();
	}
	//根据坐标画slice拓扑
	drawTopology(conti);
}

//入口，确定是首页拓扑还是slice编辑页面拓扑，获取slice_id
$(document).ready(function() {
	topology_type = $("#topology_type").text();
	if(topology_type == 0){
		//var slice_num = $("#slice_num").text();
		//var slice_ids = new Array();
		//if(slice_num == 0){
	//
		//}else if(slice_num == 1){			
		//	slice_ids[0] = $("#slice_id1").text();						
		//}else if(slice_num == 2){
		//	slice_ids[0] = $("#slice_id1").text();
		//	slice_ids[1] = $("#slice_id2").text();
		//}else if(slice_num == 3){
		//	slice_ids[0] = $("#slice_id1").text();
		//	slice_ids[1] = $("#slice_id2").text();
		//	slice_ids[2] = $("#slice_id3").text();
		//}else if(slice_num == 4){
		//	slice_ids[0] = $("#slice_id1").text();
		//	slice_ids[1] = $("#slice_id2").text();
		//	slice_ids[2] = $("#slice_id3").text();
		//	slice_ids[3] = $("#slice_id4").text();		
		//}	
		home_show_slice();
	}
	else{
		slice_id = $("#slice_id").text();
		draw(-1);
	}
//	setInterval("draw()",3000);
//	draw();
});

function f(){
	for(var i = 0; i < 14; i++){
		draw();
		rootIndex++;
	}	
}


//首页slice拓扑展示
function home_show_slice(){
	check_url = "http://" + window.location.host + "/slice/get_show_slices/";
	var str;
    $.ajax({
        type: "GET",
        url: check_url,
        dataType: "json",
        cache: false,
        async: false,  
        success: function(data) {
        	slices = data.slices;
        	if(slices && slices.length>0){
        		//alert(1);
        		$("div#slice_show").empty();
				str = "";
				str = str + "<div class=\"dg-wrapper\">";
    			for(var i=0;i<slices.length;i++){
					str = str + "<a href=\"#\">"
						+ "<div class=\"slice_content\" id=\"content"+slices[i].id+"\" style=\"height:260px; top:41px\" alt=\"image"+i+"\">"
						+ "</div>"
						+ "<div>"+slices[i].name+"拓扑图</div>"
						+ "</a>";
				}
				if(slices.length==1){
					str = str + "<a href=\"#\">"
						+ "</a>";
					str = str + "<a href=\"#\">"
						+ "</a>";
				}
				if(slices.length==2){
					str = str + "<a href=\"#\">"
						+ "</a>";
				}
				str = str + "</div>"
					+ "<nav>"	
					+ "<span class=\"dg-prev\">&lt;</span>"
					+ "<span class=\"dg-next\">&gt;</span>"
					+ "</nav>";
				$("div#slice_show").append(str);
				
				//画拓扑
				for(var i=0;i<slices.length;i++){
					draw(slices[i].id);
				}		
        	}
        	else{
        		//alert(2);
        		$("div#slice_show").empty();
        		str = "";
				str = str + "<div class=\"dg-wrapper\">";
        		str = str + "<a href=\"#\">"
					+ "</a>";
				str = str + "<a href=\"#\">"
					+ "</a>";
				str = str + "<a href=\"#\">"
					+ "</a>";
				str = str + "</div>"
					+ "<nav>"	
					+ "<span class=\"dg-prev\">&lt;</span>"
					+ "<span class=\"dg-next\">&gt;</span>"
					+ "</nav>";
				$("div#slice_show").append(str);
        	}
        }
    });
}
