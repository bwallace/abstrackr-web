<%inherit file="../site.mako" />
<%def name="title()">Predictions for Remaining Citations</%def>
    
    % if 'prob_plot_url' not in dir(c):
      <script type="text/javascript" src="https://www.google.com/jsapi"></script>
      <script type="text/javascript">
          // we will phase this code out eventually in favor of always showing
          // probability estimates
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
    % endif

  <body>
  
  <div class="content">

    <h2>${c.review_being_predicted}</h2>
    ${len(c.predictions_for_review)} citations have not been screened yet.<br />
    ${c.probably_included} citations are probably relevant.<br /><br /><br/>
    <br/><br/>
    <center><div id="chart_div" style="width: 1000px; height: 550px;">
    % if 'prob_plot_url' in dir(c):
      <center>
        <img src= "${c.prob_plot_url}">
      </center>
    % endif

    
    % if c.preds_download_url is not None:
      <right>
      <a href = "${c.preds_download_url}"><img src = "../../export_sm.png"/> download predictions</a>
      </right>
    % endif

    </div></center>
  </div>
  </body>