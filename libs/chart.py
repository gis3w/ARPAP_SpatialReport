import json

class base(object):
    
    linkCSS = '<link href="nvd3/nv.d3.css" rel="stylesheet" type="text/css">'
    baseJsScript = '''
            <script src="nvd3/lib/d3.v3.js"></script>
            <script type="text/javascript" src="nvd3/nv.d3.js"></script>
    '''
    modelsJsScript = utilsJsScript = toolsJsScript = ''
    chartData = dict()
    
    def __init__(self):
        self.setModelsScript()
        self.setUtilsScript()
        self.setToolsScript()
    
    def getCSS(self):
        return self.linkCSS
    
    def getJsScript(self):
        jsScript = self.baseJsScript + self.toolsJsScript + self.utilsJsScript + self.modelsJsScript
        return jsScript
    
    def setModelsScript(self):
        pass
    
    def setUtilsScript(self):
        pass
    
    def setToolsScript(self):
        pass
    
    def buildJsChart(self):
        pass
    
    def setData(self,data):
        self.chartData = json.dumps(data)
        return self
    
    def getChartData(self):
        return ' chartData = ' + self.chartData + ';'
    
    def getHTML(self):
        body = '''
        <div id="chart">
            <svg></svg>
        </div>
        '''
        html = self.getCSS() + body + self.getJsScript() + self.buildJsChart()
        return html
    
class bar(base):
    
    def setModelsScript(self):
        self.modelsJsScript = '''
        <script src="nvd3/src/models/axis.js"></script>
        <script src="nvd3/src/models/discreteBar.js"></script>
        <script src="nvd3/src/models/discreteBarChart.js"></script>
        '''
    def setUtilsScript(self):
        self.utilsJsScript = '''
        <script src="nvd3/src/utils.js"></script>
        '''
    def setToolsScript(self):
        self.toolsJsScript = '''
        <script src="nvd3/src/tooltip.js"></script>
        '''
    def buildJsChart(self):
        return '<script>' + self.getChartData() + '''
        nv.addGraph(function() {
          var chart = nv.models.discreteBarChart()
              .x(function(d) { return d.label })
              .y(function(d) { return d.value })
              .staggerLabels(true)
              //.staggerLabels(historicalBarChart[0].values.length > 8)
              .tooltips(true)
              .showValues(true)
              .transitionDuration(250)
              ;
          d3.select('#chart svg')
              .datum(chartData)
              .call(chart);
          nv.utils.windowResize(chart.update);
          return chart;
        });
        </script>
        '''

class pie(base):
    def setModelsScript(self):
        self.modelsJsScript = '''
        <script src="nvd3/src/models/legend.js"></script>
        <script src="nvd3/src/models/pie.js"></script>
        <script src="nvd3/src/models/pieChart.js"></script>
        '''
    def setUtilsScript(self):
        self.utilsJsScript = '''
        <script src="nvd3/src/utils.js"></script>
        '''
    def buildJsChart(self):
        return '<script>' + self.getChartData() + '''
        chart = ''
        nv.addGraph(function() {
          var width = nv.utils.windowSize().width,
          height = nv.utils.windowSize().height;
          chart = nv.models.pieChart()
                .x(function(d) { return d.key })
                .y(function(d) { return d.y })
                .width(width)
                .height(width);
              
          d3.select('#chart svg')
              .datum(chartData)
              .attr('width', width)
              .attr('height', width)
              .call(chart);
          
          return chart;
        });
        </script>
        '''
    