function treeBoxes(treeData) {
  // Calculate total nodes, max label length
  var totalNodes = 0;
  var maxLabelLength = 0;

  // Set the dimensions and margins of the diagram
  var margin = { top: 20, right: 90, bottom: 30, left: 90 },
    width = $(document).width() - margin.left - margin.right,
    height = $(document).height() - margin.top - margin.bottom;

  // Misc. variables
  var i = 0,
    duration = 750,
    root;

  var treemap;

  var zoomListener = d3.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

  // append the svg object to the body of the page
  // appends a 'group' element to 'svg'
  // moves the 'group' element to the top left margin
  var baseSvg = d3
    .select("#tree-container")
    .append("svg")
    .attr("style", "padding-top: 40px")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .attr("class", "overlay")
    .call(zoomListener);

  var svgGroup = baseSvg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // declares a tree layout and assigns the size
  treemap = d3
    .tree()
    .separation(function (a, b) {
      return a.parent == root && b.parent == root ? 3 : 1;
    })
    .size([height, width]);

  // Assigns parent, children, height, depth
  root = d3.hierarchy(treeData, function (d) {
    return d.children;
  });
  root.x0 = 0;
  root.y0 = 0;

  // Collapse after the second level
  root.children !== "undefined" ?? root.children.forEach(collapse);

  update(root);
  window.location.href.split("/")[4] === "pis" && smallScaleDiagram()
  window.location.href.split("/")[4] === "pis_diagram" && centerNode(root);

  function smallScaleDiagram() {
    svgGroup.attr("transform", d3.zoomIdentity.translate(430, 250).scale(0.22))
  }

  // A recursive helper function for performing some setup by walking through all nodes
  function visit(parent, visitFn, childrenFn) {
    if (!parent) return;
    visitFn(parent);
    var children = childrenFn(parent);
    if (children) {
      var count = children.length;
      for (var i = 0; i < count; i++) {
        visit(children[i], visitFn, childrenFn);
      }
    }
  }

  // Collapse the node and all it's children
  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }

  // Define the zoom function for the zoomable tree
  function zoom() {
    if (d3.event.transform != null) {
      svgGroup.attr("transform", d3.event.transform);
    }
  }

  // Function to center node when clicked/dropped so node doesn't get lost when collapsing/moving with large amount of children.
  function centerNode(source) {
    t = d3.zoomTransform(baseSvg.node());
    x = -source.y0;
    y = -source.x0;
    x = x * t.k + width / 2;
    y = y * t.k + height / 2;
    d3.select("svg")
      .transition()
      .duration(duration)
      .call(zoomListener.transform, d3.zoomIdentity.translate(x, y).scale(t.k));
  }

  function update(source) {
    // Call visit function to establish maxLabelLength
    visit(
      source,
      function (d) {
        totalNodes++;
        maxLabelLength = Math.max(d.data.name.length, maxLabelLength);
      },
      function (d) {
        return d.children && d.children.length > 0 ? d.children : null;
      }
    );

    var levelWidth = [1];
    var childCount = function (level, n) {
      if (n.children && n.children.length > 0) {
        if (levelWidth.length <= level + 1) levelWidth.push(0);

        levelWidth[level + 1] += n.children.length;
        n.children.forEach(function (d) {
          childCount(level + 1, d);
        });
      }
    };
    childCount(0, root);
    var newHeight = d3.max(levelWidth) * 250; // 25 pixels per line

    treemap = d3.tree().size([newHeight, width]);

    // Assigns the x and y position for the nodes
    var treeData = treemap(root);

    // Compute the new tree layout.
    var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    nodes.forEach(function (d) {
      d.y = d.depth * (maxLabelLength * 10); //maxLabelLength * 10px
    });

    // ****************** Nodes section ***************************

    // Update the nodes...
    var node = svgGroup.selectAll("g.node").data(nodes, function (d) {
      return d.id || (d.id = ++i);
    });

    // Enter any new modes at the parent's previous position.
    var nodeEnter = node
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", function (d) {
        return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on("click", click);

    var rectHeight = 50,
      rectWidth = "panjangteks",
      panjangteks = 380;

    // Create Tooltip

    var tooltip = d3
      .select("body")
      .append("div")
      .style("width", "relative")
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("background", "black")
      .style("padding", "15px")
      .style("border-radius", "10px")
      .style("font-size", "12px")
      .style("color", "white");

    nodeEnter
      .append("rect")
      .attr("class", "node")
      .attr("width", panjangteks)
      .attr("max-width", panjangteks)
      .attr("height", rectHeight)
      .attr("x", -3)
      .attr("y", (rectHeight / 2) * -1)
      .attr("rx", "15")
      .style("fill", function (d) {
        return d.data.fill;
      })
      .on("mouseover", function (d) {
        tooltip.text("Data: Coba data kalau agak panjang tes coba data panjang lorem ipsum");
        return tooltip.style("visibility", "visible");
      })
      .on("mousemove", function () {
        return tooltip.style("top", d3.event.pageY - 10 + "px").style("left", d3.event.pageX + 10 + "px");
      })
      .on("mouseout", function () {
        return tooltip.style("visibility", "hidden");
      });

    // Add labels for the nodes
    nodeEnter
      .append("text")
      .attr("x", function (d) {
        return 10;
      })
      .attr("text-anchor", function (d) {
        return "start";
      })
      .text(function (d) {
        return d.data.name;
      })
      .style("fill", "white")
      .style("font-size", "1em")
      .style("font-weight", "bold")
      .attr("dy", ".7em")
      .style("max-width", panjangteks)
      .style("position", "center");

    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);

    // Transition to the proper position for the node
    nodeUpdate
      .transition()
      .duration(duration)
      .attr("transform", function (d) {
        return "translate(" + d.y + "," + d.x + ")";
      });

    // Update the node attributes and style
    nodeUpdate
      .select("circle.node")
      .attr("r", 10)
      .style("fill", function (d) {
        return d._children ? "lightsteelblue" : "#fff";
      })
      .attr("cursor", "pointer");

    // Remove any exiting nodes
    var nodeExit = node
      .exit()
      .transition()
      .duration(duration)
      .attr("transform", function (d) {
        return "translate(" + source.y + "," + source.x + ")";
      })
      .remove();

    // On exit reduce the node circles size to 0
    nodeExit.select("circle").attr("r", 1e-6);

    // On exit reduce the opacity of text labels
    nodeExit.select("text").style("fill-opacity", 1e-6);

    // ****************** links section ***************************

    // Update the links...
    var link = svgGroup.selectAll("path.link").data(links, function (d) {
      return d.id;
    });

    // Enter any new links at the parent's previous position.
    var linkEnter = link
      .enter()
      .insert("path", "g")
      .attr("class", "link")
      .attr("d", function (d) {
        var o = { x: source.x0, y: source.y0 };
        return diagonal(o, o);
      })
      .on('click', clickLink);

    // UPDATE
    var linkUpdate = linkEnter.merge(link);

    // Transition back to the parent element position
    linkUpdate
      .transition()
      .duration(duration)
      .attr("d", function (d) {
        return diagonal(d, d.parent);
      });

    // Remove any exiting links
    var linkExit = link
      .exit()
      .transition()
      .duration(duration)
      .attr("d", function (d) {
        var o = { x: source.x, y: source.y };
        return diagonal(o, o);
      })
      .remove();

    // Store the old positions for transition.
    nodes.forEach(function (d) {
      d.x0 = d.x;
      d.y0 = d.y;
    });

    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {
      path = `M ${s.y} ${s.x}
      C ${(s.y + d.y) / 2} ${s.x},
        ${(s.y + d.y) / 2} ${d.x},
        ${d.y} ${d.x}`;

      return path;
    }

    function clickLink(d) {
      window.location.href.split("/")[4] === "pis_diagram" && centerNode(d);
    }

    // Toggle children on click.
    function click(d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }
      update(d);
      window.location.href.split("/")[4] === "pis_diagram" && centerNode(d);
    }
  }
}
