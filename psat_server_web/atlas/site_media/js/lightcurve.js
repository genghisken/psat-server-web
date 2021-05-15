// 2012-07-01 KWS Javascript Lightcurve Plotting code using Flot.

// Javascript code to plot the lightcurves.  NOTE that it gets its data
// a data variable in the calling page.  The trick is setting that data
// correctly.
//
// This code is free of HTML tags, with the exception of <DIV>.
//
// The code requires the following data to be set in the calling HTML:
//
// * jslcdata - an array of filter arrays - e.g. for each filter do this...
//              jslcdata.push([[55973.492, 20.4057, 0.024156], [55973.4929, 20.3998, 0.022031]]);
//
// * jslabels - an array of labels - the same length as the array of filters - e.g.
//              jslabels.push("g");
//
// * jslclimits - a dictionary of limit values, currently xmin, xmax, ymin, ymax,
//                discoveryDate and today.

// (There's a minor bug in the errorbars code. If errobars is switched on,
// it resets the y axis limits to show the zero mark if the error data is empty
// so now if there's no data don't bother setting the errorbars.)

// 2013-02-06 KWS Wrap the entire code in an anonymous function block. This forces
//                everything within here into a different scope.  It means that the
//                plot code can be called multiple times on the same page without
//                worrying about variable name clashes.

(function () {

// First of all, setup some global variable based on data min and max to
// setup the padding on the graph and the x2 axis. This is done here, rather
// than in the calling page, because the padding, etc is presentation specific.

// GLOBAL VARIABLES BEGIN

// Need to set the div ID from the global data
var locallcdivname = lcdivname;
var lightcurve = $(locallcdivname);

// Always refer to the external data via the global variable and lcdivname.
// Setting a local variable to this doesn't work (for reasons yet to be
// explained.

var pad = 20.0; // i.e. 5 percent
var xpadding = (jslimitsglobal[locallcdivname]["today"] - jslimitsglobal[locallcdivname]["xmin"])/pad;
var xmin = jslimitsglobal[locallcdivname]["xmin"] - xpadding;
var xmax = jslimitsglobal[locallcdivname]["xmax"] + xpadding;
var x2min = jslimitsglobal[locallcdivname]["xmin"] - jslimitsglobal[locallcdivname]["discoveryDate"] - xpadding;
var x2max = jslimitsglobal[locallcdivname]["today"] - jslimitsglobal[locallcdivname]["discoveryDate"] + xpadding;
var ymin = jslimitsglobal[locallcdivname]["ymin"];
var ymax = jslimitsglobal[locallcdivname]["ymax"];

// color palette for each data series (up to 20 at the moment)
var colors = ["#6A5ACD", //SlateBlue
              "#008000", //Green
              "#DAA520", //GoldenRod
              "#A0522D", //Sienna
              "#FF69B4", //HotPink
              "#DC143C", //Crimson
              "#708090", //SlateGray
              "#FFD700", //Gold
              "#0000FF", //Blue
              "#4B0082", //Indigo
              "#800080", //Purple
              "#008B8B", //DarkCyan
              "#FF8C00", //Darkorange
              "#A52A2A", //Brown
              "#DB7093", //PaleVioletRed
              "#800000", //Maroon
              "#B22222", //FireBrick
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


// Plot the lightcurve in a callable function

function plotlc(ptdata, ptlabels)
{
  var plotdirective = new Array();

  for(i=0; i<ptdata.length; i++)
  {
    var points = plot_options(ptdata[i]);
    if (ptlabels[i]["label"].charAt(0) == "-")
    {
      points["symbol"] = "diamond";
    }
    var obj = {
                data: ptdata[i],
                color: colors[ptlabels[i]["color"]],
                points: points
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
  lightcurve.on("plothover", function (event, pos, item) {
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

// We only want to invert the y-axis when plotting flux

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


function getYaxisParams(plotname)
{
  yparams = {}
  if (plotname == "#flot-lightcurve-forced-flux")
  {
    yparams = {
      color: plotColors["axisColor"],
      tickColor: plotColors["tickColor"],
      axisLabel: 'Flux',
      autoscaleMargin: 0.1
    }
  }
  else
  {
    yparams = {
      color: plotColors["axisColor"],
      tickColor: plotColors["tickColor"],
      // The is mag data so invert the y axis
      transform: function (v) { return -v; },
      inverseTransform: function (v) { return -v; },
      axisLabel: 'Apparent PSF Magnitude',
      min: ymin,
      max: ymax,
      autoscaleMargin: 0.1
      //autoscaleMargin: 0.1
    }
  }
  return yparams
}



// The main body of code that does the actual plotting. The lightcurve
// is plotted at the named div (lightcurve = flot-lightcurve).

// Set the options inside a variable.  We'll override a few of them for zooming.
var options = {
  grid: {
    show: true,
    backgroundColor: plotColors["backgroundColor"],
    hoverable: true,
    markings: [
        {xaxis: {from: jslimitsglobal[locallcdivname]["today"], to: xmax}, color: plotColors["shadingColor"]},
        {xaxis: {from: jslimitsglobal[locallcdivname]["today"], to: jslimitsglobal[locallcdivname]["today"]}, color: plotColors["todaylineColor"]}
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
              axisLabel: getX2axisLabel(locallcdivname)
           }
  ],
  yaxis: getYaxisParams(locallcdivname),
  legend: {
    show: true,
    position: "ne",
    // Position the legend outside the plot
    // margin: [650, 0]
    margin: [-35, 0]
  },
  selection: { 
    mode: "x" 
  }
};


var plot = $.plot(
 lightcurve,
 plotlc(jslcdataglobal[locallcdivname], jslabelsglobal[locallcdivname]),
 options
 );


$(function (){
   lightcurve.on("plotselected", function (event, ranges) {
   plot = $.plot(lightcurve,
                 plotlc(jslcdataglobal[locallcdivname], jslabelsglobal[locallcdivname]),
                 $.extend(true, {}, options, {
                   legend: {
                     show: true,
                     position: "ne",
                     // margin: [650, 0]
                     margin: [-35, 0]
                   },
                   grid: {
                     show: true,
                     backgroundColor: plotColors["backgroundColor"],
                     hoverable: true,
                     markings: [
                         {xaxis: {from: jslimitsglobal[locallcdivname]["today"], to: xmax}, color: plotColors["shadingColor"]},
                         {xaxis: {from: jslimitsglobal[locallcdivname]["today"], to: jslimitsglobal[locallcdivname]["today"]}, color: plotColors["todaylineColor"]}
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
                             axisLabel: getX2axisLabel(locallcdivname)
                           }],
                   yaxis: getYaxisParams(locallcdivname)
                 }));
   });
});


// 2013-02-06 KWS End of the anonymous function block.
})();
