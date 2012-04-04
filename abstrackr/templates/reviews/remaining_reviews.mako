<%inherit file="../site.mako" />
<%def name="title()">Predictions for Remaining Citations</%def>

    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Number of Votes');
        data.addColumn('number', 'predicted # of relevant citations');
        data.addRows([
          ['0', ${c.frequencies[0]}],
          ['1', ${c.frequencies[1]}],
          ['2', ${c.frequencies[2]}],
          ['3', ${c.frequencies[3]}],
          ['4', ${c.frequencies[4]}],
          ['5', ${c.frequencies[5]}],
          ['6', ${c.frequencies[6]}],
          ['7', ${c.frequencies[7]}],
          ['8', ${c.frequencies[8]}],
          ['9', ${c.frequencies[9]}],
          ['10', ${c.frequencies[10]}],
          ['11', ${c.frequencies[11]}]
        ]);

        var options = {
          title: 'predictions for the remaining (unscreened) citations in the review',
          hAxis: {title: 'likelihood of being relevant (11=most likely)', titleTextStyle: {color: 'red'}}
        };

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>

  <body>
  
  <div class="content">
    Review Name: ${c.review_being_predicted}<br />
    ${len(c.predictions_for_review)} citations have not been screened yet.<br />
    ${c.probably_included} citations are probably relevant.<br /><br />

    <center><div id="chart_div" style="width: 1000px; height: 700px;"></div></center>
  </div>
  </body>