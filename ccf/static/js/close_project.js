$(function(){
    judgeProject();
    $(".close").click(function(){
        judgeProject();
    });
});
//项目管理页面，项目展示部分切换
function judgeProject(){
    if($(".example-sites li").length==0){
        $(".example-sites").hide();
        $(".nothing_tip").show();
        $(".view_more").hide();        
    } else {
        $(".nothing_tip").hide();
        if($(".example-sites li").length>4){
            $(".view_more").show();   
        }
    }
}