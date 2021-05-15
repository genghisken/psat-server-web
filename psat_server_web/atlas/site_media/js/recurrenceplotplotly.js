// 2013-02-15 KWS Javascript Recurrence Plotting code using Plotly.
// * jsrecurrencedata - an array of colour arrays - e.g. for each colour do this...
//                 jsrecurrencedata.push([[55973.492, 0.4057, 0.024156], [55973.4929, 0.3998, 0.022031]]);
//
// * jsrecurrencelabels - an array of labels - the same length as the array of colours - e.g.
//                   jsrecurrencelabels.push("g-r");
//
// * jsrecurrencelimits - a dictionary of limit values, currently xmin, xmax, ymin, ymax,


// First of all, setup some global variable based on data min and max to
// setup the padding on the graph and the x2 axis. This is done here, rather
// than in the calling page, because the padding, etc is presentation specific.

(function () {

// GLOBAL VARIABLES BEGIN. Keep the same as in the lightcurve pages except for y values.
var localrecurrencedivname = recdivname;
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
var colorpalette = ["#6A5ACD", //SlateBlue
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

// GLOBAL VARIABLES END
var recdata = [];

// So... Flot wanted [[x, y, error], [x, y, error], ...]
// Plotly wants [x, x, ...], [y, y, ...], [error, error, ...]. Should be easy to convert,
// but it's a bit of a pain!


// 2018-06-27 KWS Replace this code with a Circle of the correct
//                radius as soon as I've figured out how to do it!!
function plotCircle(radius, colour) {
  //var circleOptions = {"label": "Circle", "display": false, "color":colour};
  var xarray = [];
  var yarray = [];

  var increment = Math.PI/20;
  for (var angle = 0; angle <= (2 * Math.PI); angle += increment) {
    var x = radius * Math.sin(angle);
    var y = radius * Math.cos(angle);
    xarray.push(x);
    yarray.push(y);
    }

  var circleOptions = {
    x: xarray,
    y: yarray,
    type: 'line',
    showlegend: false,
    line: {
      width: 0.5,
      color: colour
    },
    opacity: 0.4
  }
  return(circleOptions);
}


// Plot the recurrence plot in a callable function

function plotrecurrences(ptdata, ptlabels)
{
  // Three sets of data. The central point, the mean position, the scatter data
  for(i=0; i<ptdata.length; i++)
  {
    // Split out the data for each plot into separate x and y arrays
    var xarray = [];
    var yarray = [];
    for(j=0; j<ptdata[i].length; j++){
        xarray.push(ptdata[i][j][0]);
        yarray.push(ptdata[i][j][1]);
      }

    var dataOptions = {
    x: xarray,
    y: yarray,
    showlegend: false,
    type: 'scatter',
    mode: 'markers',
    name: ptlabels[i]["label"],
    marker: {
        color: colorpalette[ptlabels[i]['color']],
        opacity: 0.4,
        symbol: 'circle',
        line: {
            width: 0,
            color: 'black',
            },
            size: recmarkersize
        }
    };

    if (ptlabels[i]["display"])
    {
      dataOptions["showlegend"] = true;
    }

    recdata.push(dataOptions);
  }
}


recdata.push(plotCircle(1.0, colorpalette[5]));
recdata.push(plotCircle(3.6, colorpalette[25]));
recdata.push(plotCircle(8.0, colorpalette[19])); 

plotrecurrences(jsrecurrencedataglobal[localrecurrencedivname], jsrecurrencelabelsglobal[localrecurrencedivname]);

if (typeof lcplotwidth !== 'undefined')
{
  rw = recplotheight;
}
else
{
  rw = 0.9 * $(localrecurrencedivname).innerWidth();
  if (rw > recplotmaxwidth)
  {
    rw = recplotmaxwidth;
  }
}

// 2018-09-07 KWS Still experimenting with legend and layout. Use scaleanchor to force
//                1:1 aspect ratio, so circles are always circular!
var layout = { xaxis: {range: [jsrecurrencelimits["xmin"], jsrecurrencelimits["xmax"]], title: "\u0394RA / arcsec"},
               yaxis: {range: [jsrecurrencelimits["ymin"], jsrecurrencelimits["ymax"]], title: "\u0394Dec / arcsec", scaleanchor: "x"},
               hovermode: false,
               margin: {l: 30, r: 0, b: 0, t: 0},
               width: rw,
               height: 2.1*rw,
               paper_bgcolor: 'rgba(0,0,0,0)',
               plot_bgcolor: 'rgba(0,0,0,0)',
               legend:{
                   xanchor:"left",
                   yanchor:"bottom",
                   font: {size: 7},
                   y: -0.9,
                   x: 0
                 },
              }

Plotly.newPlot(localrecurrencedivname.replace('#',''), recdata, layout, {displayModeBar: false});

// Resize all the recurrence plots when the window size is changed.
$(window).bind("resize.recplot", function() {
  Object.keys(jsrecurrencedataglobal).forEach(function(key) {
    if (typeof recplotheight !== 'undefined')
    {
      rw = recplotheight;
      // No need to resize - do nothing.
    }
    else
    {
      rw = 0.9 * $(localrecurrencedivname).innerWidth();
      if (rw > recplotmaxwidth)
      {
        rw = recplotmaxwidth;
      }
      Plotly.relayout(key.replace('#',''), {
        margin: {l: 30, r: 0, b: 0, t: 0},
        width: rw,
        height: 2.1*rw,
        legend:{
            xanchor:"left",
            yanchor:"bottom",
            font: {size: 7},
            y: -0.9,
            x: 0
          },
      })
    }

  });
});

//console.log(recdata);
})();
