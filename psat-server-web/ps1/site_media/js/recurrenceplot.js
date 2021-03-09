// 2013-02-15 KWS Javascript Recurrence Plotting code using Flot.

// This code is free of HTML tags, with the exception of <DIV>.
//
// The code requires the following data to be set in the calling HTML:
//
// * jsrecurrencedata - an array of colour arrays - e.g. for each colour do this...
//                 jsrecurrencedata.push([[55973.492, 0.4057, 0.024156], [55973.4929, 0.3998, 0.022031]]);
//
// * jsrecurrencelabels - an array of labels - the same length as the array of colours - e.g.
//                   jsrecurrencelabels.push("g-r");
//
// * jsrecurrencelimits - a dictionary of limit values, currently xmin, xmax, ymin, ymax,

(function () {

// First of all, setup some global variable based on data min and max to
// setup the padding on the graph and the x2 axis. This is done here, rather
// than in the calling page, because the padding, etc is presentation specific.

// GLOBAL VARIABLES BEGIN. Keep the same as in the lightcurve pages except for y values.
var localrecurrencedivname = recdivname;
var recurrenceplot = $(localrecurrencedivname);
var pad = 20.0; // i.e. 5 percent
var padding = (jsrecurrencelimitsglobal[localrecurrencedivname]["xmax"] - jsrecurrencelimitsglobal[localrecurrencedivname]["xmin"])/pad;
var xmin = jsrecurrencelimitsglobal[localrecurrencedivname]["xmin"] - padding;
var xmax = jsrecurrencelimitsglobal[localrecurrencedivname]["xmax"] + padding;

var ymin = jsrecurrencelimitsglobal[localrecurrencedivname]["ymin"] - padding;
var ymax = jsrecurrencelimitsglobal[localrecurrencedivname]["ymax"] + padding;

//var pad = 20.0; // i.e. 5 percent
//var padding = (jsrecurrencelimits["xmax"] - jsrecurrencelimits["xmin"])/pad;
//var xmin = jsrecurrencelimits["xmin"] - padding;
//var xmax = jsrecurrencelimits["xmax"] + padding;

//var ymin = jsrecurrencelimits["ymin"] - padding;
//var ymax = jsrecurrencelimits["ymax"] + padding;

// colour palette for each data series (up to 26 at the moment)
var colorpallette = ["#6A5ACD", //SlateBlue
                     "#008000", //Green
                     "#DAA520", //GoldenRod
                     "#A0522D", //Sienna
                     "#FF69B4", //HotPink
                     "#DC143C", //Crimson
                     "#FF8C00", //Darkorange
                     "#FFD700", //Gold
                     "#0000CD", //MediumBlue
                     "#4B0082", //Indigo
                     "#800080", //Purple
                     "#A52A2A", //Brown
                     "#DB7093", //PaleVioletRed
                     "#708090", //SlateGray
                     "#800000", //Maroon
                     "#B22222", //FireBrick
                     "#008B8B", //DarkCyan
                     "#9ACD32", //YellowGreen
                     "#FA8072", //Salmon
                     "#000000", //Black
                     "#6495ED", // CornflowerBlue
                     "#0000FF", // Blue
                     "#191970", // MidnightBlue
                     "#98FB98", // PaleGreen
                     "#FF0000", // Red
                     "#008000", // Green
                     "#F0F8FF"  // AliceBlue
                      ];

// Should feed the colorpallette form the calling page - better still, the CSS
var plotColors = { "backgroundColor": "#FFFFFF",
                   "axisColor": "#000000",
                   "tickColor": "#BFBFBF",
                   "shadingColor": "#DDDDDD",
                   "tooltipBackground": "#EEEEFF",
                   "tooltipBorder": "#FFDDDD",
                   "todaylineColor": "FF0000"};

//var recurrenceplot = $("#flot-recurrenceplot");

// GLOBAL VARIABLES END

// Unlike Gnuplot, Flot doesn't plot functions natively, so you have
// to decide on the granularity of your x data.

function plotCircle(radius, ptdata, ptlabels, colour) {
  var circleOptions = {"label": "Circle", "display": false, "color":colour};
  ptlabels.push(circleOptions);

  var increment = Math.PI/20;
  var circlePoints = new Array();
  for (var angle = 0; angle <= (2 * Math.PI); angle += increment) {
    var x = radius * Math.sin(angle);
    var y = radius * Math.cos(angle);
    circlePoints.push([x, y]);
    }
  ptdata.push(circlePoints);
}


// Set the plot options in a callable function

function plot_options(data)
{
  var points_options = {
    show: true,
    fill: true,
    fillColor: false,
    lineWidth: 1,
    radius: 5
  }

  return(points_options);
}

function circle_options()
{
  var points_options = {
    show: true,
    fill: false,
    lineWidth: 1
  }

  return(points_options);
}


// Plot the recurrence plot in a callable function

function plotrecurrences(ptdata, ptlabels)
{

  plotCircle(1.0, ptdata, ptlabels, 26);
  plotCircle(2.0, ptdata, ptlabels, 5);
  plotCircle(3.0, ptdata, ptlabels, 26);

  var plotdirective = new Array();

  for(i=0; i<ptdata.length; i++)
  {
    if (ptlabels[i]["label"] == "Circle"){
      var obj = {
                  data: ptdata[i],
                  color: colorpallette[ptlabels[i]["color"]],
                  lines: circle_options()
                }
    }
    else {
      var obj = {
                  data: ptdata[i],
                  color: colorpallette[ptlabels[i]["color"]],
                  points: plot_options(ptdata[i])
                }
    }
    if (ptlabels[i]["display"])
    {
      obj["label"] = ptlabels[i]["label"];
    }

    plotdirective.push(obj);
  }

  return (plotdirective);
}


// Tooltip code begins
// Code shows x and y when hovering over a point

function showTooltip(x, y, contents) {
  $('<div id="tooltip">' + contents + '</div>').css( {
    position: 'absolute',
    display: 'none',
    top: y - 10,
    left: x + 30,
    //border: '1px solid #fdd',
    border: '1px solid ' + plotColors["tooltipBorder"],
    padding: '2px',
    'background-color': plotColors["tooltipBackground"],
    opacity: 0.80
  }).appendTo("body").fadeIn(200);
}

$(function (){
  var previousPoint = null;
  recurrenceplot.on("plothover", function (event, pos, item) {
    $("#x").text(pos.x.toFixed(3));
    $("#y").text(pos.y.toFixed(2));

    if (item) {
      if (previousPoint != item.dataIndex) {
        previousPoint = item.dataIndex;
              
        $("#tooltip").remove();
        var x = item.datapoint[0].toFixed(3),
            y = item.datapoint[1].toFixed(2);
            
        if (item.series.label)
        {
          showTooltip(item.pageX, item.pageY,
                      item.series.label + " = " + x + " " + y);
        }
      }
    }
    else {
      $("#tooltip").remove();
      previousPoint = null;            
    }
  });
});

// Tooltip code ends


// The main body of code that does the actual plotting. The recurrenceplot
// is plotted at the named div (recurrenceplot = flot-recurrenceplot).

var options = {
  grid: {
    show: true,
    backgroundColor: plotColors["backgroundColor"],
    hoverable: false
  },
  xaxis: {
    color: plotColors["axisColor"],
    tickColor: plotColors["tickColor"],
    axisLabel: '&Delta; RA / arcsec',
    min: xmin,
    max: xmax
    //autoscaleMargin: 0.1
  },
  yaxis: {
    color: plotColors["axisColor"],
    tickColor: plotColors["tickColor"],
    // The is mag data so invert the y axis
    axisLabel: '&Delta; Dec / arcsec',
    min: ymin,
    max: ymax
  },
  legend: {
    show: true,
    position: "nw",
    margin: [210, 0]
  },
  selection: { 
    mode: "x" 
  }
};


var plot = $.plot(
  recurrenceplot,
  //plotrecurrences(jsrecurrencedata, jsrecurrencelabels),
  plotrecurrences(jsrecurrencedataglobal[localrecurrencedivname], jsrecurrencelabelsglobal[localrecurrencedivname]),
  options
 );

// 2013-02-06 KWS End of the anonymous function block.
})();
