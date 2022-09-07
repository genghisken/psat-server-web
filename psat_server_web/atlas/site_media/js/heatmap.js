// 2013-02-15 KWS Javascript Recurrence Plotting code using Plotly.
// * jsheatmapdata - an array of colour arrays - e.g. for each colour do this...
//                 jsheatmapdata.push([[55973.492, 0.4057, 0.024156], [55973.4929, 0.3998, 0.022031]]);
//
// * jsheatmaplabels - an array of labels - the same length as the array of colours - e.g.
//                   jsheatmaplabels.push("g-r");
//
// * jsheatmaplimits - a dictionary of limit values, currently xmin, xmax, ymin, ymax,


// First of all, setup some global variable based on data min and max to
// setup the padding on the graph and the x2 axis. This is done here, rather
// than in the calling page, because the padding, etc is presentation specific.

(function () {

// GLOBAL VARIABLES BEGIN. Keep the same as in the lightcurve pages except for y values.
var localheatmapdivname = heatmapdivname;
var pad = 20.0; // i.e. 5 percent
// var padding = (jsheatmaplimitsglobal[localheatmapdivname]["xmax"] - jsheatmaplimitsglobal[localheatmapdivname]["xmin"])/pad;
// var xmin = jsheatmaplimitsglobal[localheatmapdivname]["xmin"] - padding;
// var xmax = jsheatmaplimitsglobal[localheatmapdivname]["xmax"] + padding;

// var ymin = jsheatmaplimitsglobal[localheatmapdivname]["ymin"] - padding;
// var ymax = jsheatmaplimitsglobal[localheatmapdivname]["ymax"] + padding;

//var pad = 20.0; // i.e. 5 percent
//var padding = (jsheatmaplimits["xmax"] - jsheatmaplimits["xmin"])/pad;
//var xmin = jsheatmaplimits["xmin"] - padding;
//var xmax = jsheatmaplimits["xmax"] + padding;

//var ymin = jsheatmaplimits["ymin"] - padding;
//var ymax = jsheatmaplimits["ymax"] + padding;

var resolution = jsheatmapresolutionglobal[localheatmapdivname];
var colorbarspan = jsheatmapcolorbarspanglobal[localheatmapdivname];

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
var heatmapdata = [];


// Plot the heatmap plot in a callable function

function plotheatmaps(ptdata)
{
  // Three sets of data. The central point, the mean position, the scatter data

    // Split out the data for each plot into separate x and y arrays
  var dataOptions = {
  z: ptdata,
  zauto: false,
  zmin: 0,
  zmax: colorbarspan,
  type: 'heatmap',
  colorscale: 'Viridis',
  colorbar: {len: 1.0},
  name: 'heatmap'
  };

  heatmapdata.push(dataOptions);

  if (x !== null && y !== null)
  {
    var scaledx = x.map(function(a) { return (a + 0.5) * 10559.0 / resolution; })
    var scaledy = y.map(function(a) { return (a + 0.5) * 10559.0 / resolution; })

    var scatterOptions = {
    x: x,
    y: y,
    customdata: [[scaledx, scaledy]],
    hovertemplate: ('x = %{customdata[0]:.2f}, y = %{customdata[1]:.2f}'),
    mode: 'markers',
    type: 'scatter',
    name: 'location'
    };

  heatmapdata.push(scatterOptions);
  }
}



plotheatmaps(jsheatmapdataglobal[localheatmapdivname]);

if (typeof heatmapplotwidth !== 'undefined')
{
  rw = heatmapplotheight;
}
else
{
  rw = 0.9 * $(localheatmapdivname).innerWidth();
  if (rw > heatmapplotmaxwidth)
  {
    rw = heatmapplotmaxwidth;
  }
}

// 2018-09-07 KWS Still experimenting with legend and layout. Use scaleanchor to force
//                1:1 aspect ratio, so blocks are always square!
var layout = { yaxis: {scaleanchor: "x", visible: false},
               showlegend: false,
               xaxis: {visible: false},
               paper_bgcolor: 'rgba(0,0,0,0)',
               plot_bgcolor: 'rgba(0,0,0,0)',
               width: rw,
               height: rw,
              }

Plotly.newPlot(localheatmapdivname.replace('#',''), heatmapdata, layout, {displayModeBar: false});

// Resize all the heatmap plots when the window size is changed.
$(window).bind("resize.heatmapplot", function() {
  Object.keys(jsheatmapdataglobal).forEach(function(key) {
    if (typeof heatmapplotheight !== 'undefined')
    {
      rw = heatmapplotheight;
      // No need to resize - do nothing.
    }
    else
    {
      rw = 0.9 * $(localheatmapdivname).innerWidth();
      if (rw > heatmapplotmaxwidth)
      {
        rw = heatmapplotmaxwidth;
      }
      Plotly.relayout(key.replace('#',''), {
        yaxis: {scaleanchor: "x", visible: false},
        showlegend: false,
        xaxis: {visible: false},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        width: rw,
        height: rw,
      })
    }

  });
});

//console.log(heatmapdata);
})();
