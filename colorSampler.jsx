// use extractColors( list of x,y coordinate pairs) to sample colors from the document.
var Sampler = (function()
{
    function samplerRGB(sampler){
        // given a color sampler.color.rgb returns the RGB colors as a list [R,G,B]
        var red = sampler.red;
        var green = sampler.green;
        var blue = sampler.blue;
        //round floats to ints
        var RGB = [Math.round(red), Math.round(green), Math.round(blue)];
        //var RGB = [red,green,blue];//Math.round(red), Math.round(green), Math.round(blue)];
        return RGB;
    };

    function sampleColor(point){
        var _point = point; 
        sampler = app.activeDocument.colorSamplers.add(point);
        color = samplerRGB(sampler.color.rgb);
        return color;
    };

    function pointsToColors(points)
    {
        
        var colors = [];
        var i;
        var samplers = [];
        var doc = app.activeDocument
        var w = doc.width.as("px");
        var h = doc.height.as("px");
        var colorSamplers = doc.colorSamplers;
        
        for(i in points)
        {
            if (points[i][0] < w && points[i][1] < h)
            {
                var sampler = colorSamplers.add(points[i])
                samplers.push(sampler);
            } else {
                $.writeln("Sampler position outside document, skipped - ", points[i]);
            }

        }
        for (i in samplers)
        {
            colors.push(samplerRGB(samplers[i].color.rgb));
        };
        if (colorSamplers.length > 0)
        {
            colorSamplers.removeAll();
        }
        return colors;
    }

    function extractColors(points)
    {
        // extracts color for each point in points
        // [[0,0],[1,1],...] to RGB [[128,128,128],[0,0,0],...]
        var colors = []
        if (points.length > 10)
        {
        //limited to 10 samplers at once in Photoshop 14.2
            for ( var i = 0; i < points.length; i += 10)
            {
                var _points = points.slice(i,i+10);            
                var x;
                var y = pointsToColors(_points)
                for (x in y)
                {
                    colors.push(y[x]);
                }
            }
        } else {
            var x;
            var y = pointsToColors(points);
            for (x in y)
            {
                colors.push(y[x]);
            }
        }
        return colors;
    };

    // there was an optimization I wanted this function for in this module, I can't recall where...
    function joinArray(){
        var b;
        b = arguments[0];
        for (var a = 1; a < arguments.length;a++)
        {
            for(var c=0; c < arguments[a].length;c++)
            {
                b.push(arguments[a][c]);
            }
        }
        return b
    }

    function __test()
    {
        //dummy data test
        var points = new Array();
        // don't to run out of characters
        app.activeDocument.colorSamplers.removeAll();
        for (var j=0; j < 50; j++){
            points.push(Array(j,j));
            }
        var json = extractColors(points);
        $.writeln(json.length);
        $.writeln(json);
    }

    function test_arrayJoin()
    {
        var a = [];
        for (var j=0; j < 6; j++){
            a.push(Array(j,0));
            }
        $.writeln(joinArray(a));
    }
    //__test();
    //test_arrayJoin();
    //https://github.com/douglascrockford/JSON-js
    return {
        colors:extractColors,
        color:sampleColor
        }
})();