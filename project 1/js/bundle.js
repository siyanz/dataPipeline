var width = 1000,
    height = 1000,
    diameter = 1000,
    radius = diameter / 2,
    innerRadius = radius - 150;

var cluster = d3.layout.cluster()
    .size([360, innerRadius])
    .sort(null)
    .value(function(d) { return d.size; });

var bundle = d3.layout.bundle();

var line = d3.svg.line.radial()
    .interpolate("bundle")
    .tension(0.85)
    .radius(function(d) { return d.y; })
    .angle(function(d) { return d.x / 180 * Math.PI; });


var svg = d3.select("body").append("svg")
    .attr("width", diameter)
    .attr("height", diameter)
  .append("g")
    .attr("transform", "translate(" + radius + "," + radius + ")");


var link = svg.append("g").selectAll(".link"),
    node = svg.append("g").selectAll(".node");

d3.json("data/d3data.json", function(error, classes) {
  var nodes = cluster.nodes(packageHierarchy(classes.nodes)),
    links = packageImports(nodes, classes.links);

    console.log(classes.nodes.length - nodes.length);

var loading = svg.append("text")
    .attr("x", width / 2)
    .attr("y", height / 2)
    .attr("dy", ".35em")
    .style("text-anchor", "middle")
    .text("Simulating. One moment please…");

  link = link
    .data(bundle(links))
  .enter().append("path")
    .each(function(d) { d.source = d[0], d.target = d[d.length - 1]; })
    .attr("class", "link")
    .attr("d", line);

  node = node
    .data(nodes.filter(function(n) { return !n.children; }))
  .enter().append("text")
    .attr("class", "node")
    .attr("dy", ".1em")
    .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 8) + ",0)" + (d.x < 180 ? "" : "rotate(180)"); })
    .style("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
    .style("font-weight", function(d) {
      if (d.followersCount > 100000) {
        return "bold";
      }
    })
    .style("font-size", function(d) {
      if (d.followersCount > 100000) {
        return "12px";
      }
    })
    .text(function(d, i) { 
      if (d.followersCount > 100000){
        return d.userName; 
      } else{
        if (i % 4 == 2) return d.userName;
      }})
    .on("mouseover", mouseovered)
    .on("mouseout", mouseouted);

    loading.remove();
});

function mouseovered(d) {
  node
      .each(function(n) { n.target = n.source = false; });

  link
      .classed("link--target", function(l) { if (l.target === d) return l.source.source = true; })
      .classed("link--source", function(l) { if (l.source === d) return l.target.target = true; })
    .filter(function(l) { return l.target === d || l.source === d; })
      .each(function() { this.parentNode.appendChild(this); });

}

function mouseouted(d) {
  link
      .classed("link--target", false)
      .classed("link--source", false);
}

d3.select(self.frameElement).style("height", diameter + "px");

var count = 0;
// Lazily construct the package hierarchy from class names.
function packageHierarchy(classes) {
  var map = {};
  function find(name, data) {
    var node = map[name];
    if (!node) {
      node = map[name] = data || {name: name, children: []};
      if (name){
          node.parent = find("");
          node.parent.children.push(node);
          node.key = name;
        } 
    } 
    return node;
  }

  classes.forEach(function(d) {
    find(d.userId, d);
  });

  return map[""];
}

// Return a list of imports for the given array of nodes.
function packageImports(nodes, links) {
  var map = {},
      imports = [];

  // Compute a map from name to node.
  nodes.forEach(function(d) {
    map[d.userName] = d;
  });

  // For each import, construct a link from the source to target node.
  links.forEach(function(d) {
    var s = d.source,
      t = d.target;

    imports.push({source: nodes[s], target: nodes[t]});
    });
  return imports;
}
