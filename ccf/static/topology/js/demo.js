var width = 960,
    height = 800;

var color = d3.scale.category10();

var nodes = [
],
    links = [
        {source: 1, target: 2},
        {source: 2, target: 4},
        {source: 5, target: 1},
        {source: 3, target: 0},
        {source: 3, target: 2},
        {source: 1, target: 7},
        {source: 6, target: 7},
        {source: 6, target: 0},
    ];

for (var i = 0; i < islands.length; i++) {
    var island = islands[i];
    var island_node = $("<div class='island-node island-node" + i + "' data-id='" + i + "' data-title='" + island.islandname + "'></div>");
    island_node.click(function (argument) {
        var id = $(this).data('id');
        var title = $(this).data('title');
        /*var img_url = '/static/topology/img/topo-' + id + '.png';
        if ($(this).hasClass('hl')) {
            var slice_id = $(this).data('slice');
            img_url = '/static/topology/img/topo-slice-' + id + "-" + slice_id  + '.png'
        }
        $('#topo-img').attr('src', img_url);
        $('.iframe').show();
        */
        $('.iframe .form-actions h3').text(title + "网络拓扑");
        $('.topology').attr("src", "/topology/?island_id=" + (id + 1) + "&no_parent=true").load(function (argument) {
            $('.iframe').show();
        });
    });


    $('.topo-box').append(island_node);
    nodes.push({id: island.id, name: island.islandname,
        x: island.x,
        y: island.y
    });
};

var force = d3.layout.force()
    .nodes(nodes)
    .links(links)
    .charge(-1800)
    .linkDistance(200)
    .size([width, height])
    .on("tick", tick);

var svg = d3.select("#city-topo").append("svg")
    .attr("width", width)
    .attr("height", height);

var node = svg.selectAll(".node"),
    link = svg.selectAll(".link");


// 1. Add three nodes and three links.
setTimeout(function() {
  start();
}, 0);

function start() {
  link = link.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });


  link.enter().insert("line", ".node").attr("class", "link");
  link.exit().remove();

  node = node.data(force.nodes(), function(d) { return d.id;});
  node.enter().append('g');
  node.append("circle").attr("class", function(d) { return "node node" + d.id; }).attr("r", 16)
      .on('click', function  (d) {
        $('.topology').attr("src", "/topology/?island_id=" + d.id + "&no_parent=true").load(function (argument) {
            $('.iframe').show();
        });
      });
  node.attr('transform', function(d) {
    return 'translate(' + d.x + ',' + d.y + ')';
  });
  node.append('text')
       .attr("dx", 20).attr("dy", ".35em")
       .text(function(d) { return d.name});
  node.exit().remove();

  force.start();
}

var count = 0;
function tick() {
 //   node.attr('transform', function(d) {
   //     return 'translate(' + d.x + ',' + d.y + ')';
   // });
    if (count == 0) {
        link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });
        count --;
    }

}


$('.node').click(function () {
});
$('.island-button').click(function () {
    $('.iframe').hide();
    $('.island-button').removeClass('selected');
    $('.island-node').removeClass('hl').removeData('slice');
    var slice_id = $(this).data('id');
    $('#island-img').attr('src', '/static/topology/img/slice-hl-' + slice_id + '.png');

    $(this).addClass('selected');
    var islands = ("" + $(this).data('islands')).split(',');
    $('.node').css('fill', '#1f77b4');
    for (var i = 0; i < islands.length; i++) {
        var island = islands[i];
        $('.island-node').addClass('hl').data('slice', slice_id);
        $('.node' + island).css('fill', '#2ca02c');
    };
});
$('.close-button').click(function () {
    $('.iframe').hide();
});

