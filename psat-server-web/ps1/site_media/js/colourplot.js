// 2012-07-01 KWS Javascript Lightcurve Plotting code using Flot.

// Javascript code to plot the colour vs time.  NOTE that it gets its data
// a data variable in the calling page.  The trick is setting that data
// correctly.
//
// This code is free of HTML tags, with the exception of <DIV>.
//
// The code requires the following data to be set in the calling HTML:
//
// * jscolourdata - an array of colour arrays - e.g. for each colour do this...
//                 jscolourdata.push([[55973.492, 0.4057, 0.024156], [55973.4929, 0.3998, 0.022031]]);
//
// * jscolourlabels - an array of labels - the same length as the array of colours - e.g.
//                   jscolourlabels.push("g-r");
//
// * jscolourlimits - a dictionary of limit values, currently xmin, xmax, ymin, ymax,
//                discoveryDate and today.

(function () {

// First of all, setup some global variable based on data min and max to
// setup the padding on the graph and the x2 axis. This is done here, rather
// than in the calling page, because the padding, etc is presentation specific.

// GLOBAL VARIABLES BEGIN. Keep the same as in the lightcurve pages except for y values.

// Need to set the div ID from the global data
var localcolourdivname = colourdivname;
var colourplot = $(localcolourdivname);

var pad = 20.0; // i.e. 5 percent
var xpadding = (jscolourlimitsglobal[localcolourdivname]["today"] - jscolourlimitsglobal[localcolourdivname]["xmin"])/pad;
var xmin = jscolourlimitsglobal[localcolourdivname]["xmin"] - xpadding;
var xmax = jscolourlimitsglobal[localcolourdivname]["xmax"] + xpadding;
var x2min = jscolourlimitsglobal[localcolourdivname]["xmin"] - jscolourlimitsglobal[localcolourdivname]["discoveryDate"] - xpadding;
var x2max = jscolourlimitsglobal[localcolourdivname]["today"] - jscolourlimitsglobal[localcolourdivname]["discoveryDate"] + xpadding;

var ymin = jscolourlimitsglobal[localcolourdivname]["ymin"];
var ymax = jscolourlimitsglobal[localcolourdivname]["ymax"];

// colour palette for each data series (up to 20 at the moment)
var colors = ["#6A5ACD", //SlateBlue
              "#008000", //Green
              "#DAA520", //GoldenRod
              "#A0522D", //Sienna
              "#FF69B4", //HotPink
              "#DC143C", //Crimson
              "#FF8C00", //Darkorange
              "#FFD700", //Gold
              "#0000FF", //Blue
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
              "#000000"]; //Black

// Should feed the colors form the calling page - better still, the CSS
var plotColors = { "backgroundColor": "#FFFFFF",
                   "axisColor": "#000000",
                   "tickColor": "#BFBFBF",
                   "shadingColor": "#DDDDDD",
                   "tooltipBackground": "#EEEEFF",
                   "tooltipBorder": "#FFDDDD",
                   "todaylineColor": "FF0000"};


// GLOBAL VARIABLES END


// Callback function for new detection limit arrow symbols

function limitarrow(ctx, x, y, radius, shadow) {
  var size = radius * Math.sqrt(Math.PI) / 2;
  ctx.moveTo(x - size, y);
  ctx.lineTo(x + size, y);
  ctx.moveTo(x, y);
  ctx.lineTo(x, y + 7*size);
  ctx.moveTo(x - size, y + 4*size);
  ctx.lineTo(x, y + 7*size);
  ctx.lineTo(x + size, y + 4*size);
}

// End callback


// Set the plot options in a callable function

function plot_options(data)
{
  if(data.length > 0 && data[0].length > 2)
  {
    var points_options = {
      show: true,
      fill: true,
      //fillColor: "rgba(0, 0, 0, 0.4)",
      fillColor: false,
      lineWidth: 1,
      radius: 5,
      errorbars: "y",
      yerr: {show: true, upperCap: "-", lowerCap: "-", radius: 5}
    }
  }
  else
  {
    var points_options = {
      show: true,
      symbol: limitarrow
    }
  }

  return(points_options);
}


// Plot the colourplot in a callable function

function plotcolours(ptdata, ptlabels)
{
  var plotdirective = new Array();

  for(i=0; i<ptdata.length; i++)
  {
    var obj = {
                data: ptdata[i],
                color: colors[ptlabels[i]["color"]],
                points: plot_options(ptdata[i])
              }
    if (ptlabels[i]["display"])
    {
      obj["label"] = ptlabels[i]["label"];
    }

    plotdirective.push(obj);
  }

  // Try adding an empty dataset to the second x axis. The result is that
  // nothing gets plotted, but the axis gets rewritten (which is what we
  // want). The second x axis will show the days since discovery.

  var obj2 = {
               data: [],
               xaxis: 2
             }
  plotdirective.push(obj2);

  return (plotdirective);
}


// Tooltip code begins
// Code shows y and MJD when hovering over a point

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
  colourplot.on("plothover", function (event, pos, item) {
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
                      item.series.label + " = " + y + " (" + x + ")");
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


function getX2axisLabel(plotname)
{
  var x2axisTitle = '';
  if (plotname.indexOf('forced') > 0)
  {
    x2axisTitle = 'Days since Earliest Detection (Forced Photometry)';
  }
  else
  {
    x2axisTitle = 'Days since Earliest Detection';
  }
  return x2axisTitle;
}


// The main body of code that does the actual plotting. The colourplot
// is plotted at the named div (colourplot = flot-colourplot).

// Set the options inside a variable.  We'll override a few of them for zooming.
var options = {
  grid: {
    show: true,
    backgroundColor: plotColors["backgroundColor"],
    hoverable: true,
    markings: [
        {xaxis: {from: jscolourlimitsglobal[localcolourdivname]["today"], to: xmax}, color: plotColors["shadingColor"]},
        {xaxis: {from: jscolourlimitsglobal[localcolourdivname]["today"], to: jscolourlimitsglobal[localcolourdivname]["today"]}, color: plotColors["todaylineColor"]}
    ]
  },
  xaxis: {
    color: plotColors["axisColor"],
    tickColor: plotColors["tickColor"],
    axisLabel: 'MJD',
    min: xmin,
    max: xmax
    //autoscaleMargin: 0.1
  },
  xaxes: [
           {}, // Empty 1st axis - use that defined above
           {
              position: "top",
              min: x2min,
              max: x2max,
              color: plotColors["axisColor"],
              tickColor: plotColors["tickColor"],
              axisLabel: getX2axisLabel(localcolourdivname)
           }
  ],
  yaxis: {
    color: plotColors["axisColor"],
    tickColor: plotColors["tickColor"],
    // The is mag data so invert the y axis
    axisLabel: 'Colour',
    autoscaleMargin: 0.2
  },
  legend: {
    show: true,
    position: "ne",
    margin: [40, 0]
  },
  selection: { 
    mode: "x" 
  }
};


$(function (){
   colourplot.on("plotselected", function (event, ranges) {
   plot = $.plot(colourplot,
                 plotcolours(jscolourdataglobal[localcolourdivname], jscolourlabelsglobal[localcolourdivname]),
                 $.extend(true, {}, options, {
                   legend: {
                     show: true,
                     position: "ne",
                     margin: [40, 0]
                   },
                   grid: {
                     show: true,
                     backgroundColor: plotColors["backgroundColor"],
                     hoverable: true,
                     markings: [
                         {xaxis: {from: jscolourlimitsglobal[localcolourdivname]["today"], to: xmax}, color: plotColors["shadingColor"]},
                         {xaxis: {from: jscolourlimitsglobal[localcolourdivname]["today"], to: jscolourlimitsglobal[localcolourdivname]["today"]}, color: plotColors["todaylineColor"]}
                         ]
                     },
                   xaxes: [{ min: ranges.xaxis.from, max: ranges.xaxis.to,
                             color: plotColors["axisColor"],
                             tickColor: plotColors["tickColor"],
                             axisLabel: 'MJD'
                           },
                           { min: ranges.x2axis.from, max: ranges.x2axis.to,
                             position: "top",
                             color: plotColors["axisColor"],
                             tickColor: plotColors["tickColor"],
                             axisLabel: getX2axisLabel(localcolourdivname)
                           }],
                   yaxis: {
                           color: plotColors["axisColor"],
                           tickColor: plotColors["tickColor"],
                           axisLabel: 'Colour',
                           autoscaleMargin: 0.2
                          }
                 }));
   });
});


var plot = $.plot(
 colourplot,
 plotcolours(jscolourdataglobal[localcolourdivname], jscolourlabelsglobal[localcolourdivname]),
 options
 );

// 2013-02-06 KWS End of the anonymous function block.
})();
