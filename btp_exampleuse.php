<?php
$servername = "#####";
$username = "#####";
$password = "#####";
$db = "#####";
// Create connection
$conn = new mysqli($servername, $username, $password, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$pastWeek = strtotime("-1 week");
$time = date("Y-m-d",$pastWeek);

$sql = "SELECT * FROM documents WHERE DATE > '$time' AND company='microsoft'";
//echo $sql;

$result = $conn->query($sql);
//echo $result->num_rows;

//echo "What?";

$records = array();

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
      array_push($records,$row);
    }
}
$len = sizeof($records);

$positive_records = array();
$negative_records = array();

for($x=0;$x<$len;$x++){
  $tmp = (float)$records[$x]['score'];
  if( $tmp > (float)0.0){
    array_push($positive_records,$records[$x]);
  }else{
    array_push($negative_records,$records[$x]);
  }
}

$len_pos = sizeof($positive_records);
$len_neg = sizeof($negative_records);


$articles = array();
if($len_pos > $len_neg){
  for($x=0;$x<$len_pos;$x++){
    array_push($articles,$positive_records[$x]);
  }
  for($x=0;$x<$len_neg;$x++){
    array_push($articles,$negative_records[$x]);
  }
}else{
  for($x=0;$x<$len_neg;$x++){
    array_push($articles,$negative_records[$x]);
  }
  for($x=0;$x<$len_pos;$x++){
    array_push($articles,$positive_records[$x]);
  }
}
$len = sizeof($articles);
$urls = array();
for($x=0;$x<$len;$x++){
  $url = $articles[$x]['url'];
  $sentence = "python data_extractor/textGenerator.py '$url'";
  $output = exec($sentence,$retval);
  $output = "...".substr($output, 100, 350)."...";
  array_push($urls,$output);
}
?>


<!DOCTYPE html>
<!--[if IE 8]> <html lang="en" class="ie8"> <![endif]-->
<!--[if IE 9]> <html lang="en" class="ie9"> <![endif]-->
<!--[if !IE]><!--> <html lang="en"> <!--<![endif]-->
<head>
    <title>B.Tech Project</title>
    <!-- Meta -->
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Responsive HTML5 Website landing Page for Developers">
    <meta name="author" content="3rd Wave Media">
    <link rel="shortcut icon" href="favicon.ico">
    <link href='http://fonts.googleapis.com/css?family=Lato:300,400,300italic,400italic' rel='stylesheet' type='text/css'>
    <link href='http://fonts.googleapis.com/css?family=Montserrat:400,700' rel='stylesheet' type='text/css'>
    <!-- Global CSS -->
    <link rel="stylesheet" href="assets/plugins/bootstrap/css/bootstrap.min.css">
    <!-- Plugins CSS -->
    <link rel="stylesheet" href="assets/plugins/font-awesome/css/font-awesome.css">
    <!-- github acitivity css -->
    <link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/octicons/2.0.2/octicons.min.css">
    <link rel="stylesheet" href="http://caseyscarborough.github.io/github-activity/github-activity-0.1.0.min.css">

    <!-- Theme CSS -->
    <link id="theme-style" rel="stylesheet" href="assets/css/styles.css">
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
    <!-- Load c3.css -->
			<link href="/developer/c3js/c3js/c3-0.4.11/c3.css" rel="stylesheet" type="text/css">

			<!-- Load d3.js and c3.js -->

			<script src="/developer/c3js/c3js/c3-0.4.11/d3.v3.min.js" charset="utf-8"></script>
			<script src="/developer/c3js/c3js/c3-0.4.11/c3.min.js"></script>


    <style type="text/css">
      .content-true {
        background-color: #dae3e7 ;
        height: 250px;
        border: 2px  #000;
        border-radius: 5px;
        -moz-border-radius: 5px;
      }
      .content-false {
        background-color: #dae3e7 ;
        height: 250px;
        border: 2px  #000;
        border-radius: 5px;
        -moz-border-radius: 5px;
      }
      .container{
        margin:  30px auto;
      }
    </style>

</head>



<body>
    <!-- ******HEADER****** -->
    <header class="header">
        <div class="container">
            <img class="profile-image img-responsive pull-left" src="assets/images/stock1.png" alt="James Lee" />
            <div class="profile-content pull-left">
                <h1 class="name">Stock Advisor</h1>
                <h2 class="desc">Data Analytics in Stock Market</h2>
                <h3 class="descz">Nikhil Molangur</h3>
            </div><!--//profile-->
            <a class="btn btn-cta-primary pull-right" href="https://github.com/nikhm" target="_blank"><i class="fa fa-paper-plane"></i>Documentation</a>
        </div><!--//container-->
    </header><!--//header-->

    <div class="container sections-wrapper">
        <div class="row">
            <div class="primary col-md-9 col-sm-12 col-xs-12">
                <section class="about section">
                    <div class="section-inner">
                      <div id="chart"></div>
                      <script>
                      var chart = c3.generate({
                          bindto: '#chart',
                          data: {
                            columns: [
                              ['Predicted price', 0.18173200685308713, -0.025636706019972214, 0.10494126018865003, 0.048857901480392776, 0.095447748364147142, -0.0017624844473126565, -0.2563038368473769, -0.71591077393149205, -0.13895500191169902, -0.33510986741449761, -0.45073132025664897, 0.057487736638840492, -0.14816064068846097, 0.58410397799231661, 1.0,
                                                  0.19916806690288602, -0.15055814957413127, -0.13957217912170872, -0.15730695138374456, -0.17380073083528497],
                              ['Stock price', 0.18173200685308713, -0.025636706019972214, 0.10494126018865003, 0.048857901480392776, 0.095447748364147142, -0.0017624844473126565, -0.2563038368473769, -0.71591077393149205, -0.13895500191169902, -0.33510986741449761, -0.45073132025664897, 0.057487736638840492, -0.14816064068846097, 0.58410397799231661, 1.0]
                            ]
                          }
                      });
                      </script>
                    </div><!--//section-inner-->
                </section><!--//section-->

               <section class="latest section">
                    <div class="section-inner">

                      <div><h2> News </h2></div>
                      <!-- Nikhil -->
                      <!--
                        We have got positive_records and negative_records containing the articles
                        of company for past week.
                      -->
                      <?php
                      $len = sizeof($articles);
                      for($x=0;$x<$len;$x+=2){
                        //$statement = "<div class='kill'>Hello!</div>";
                        $statement =   "<div class='container'>".
                           "<div class='row'>".
                             "<div class='col-xs-4'>".
                               "<div class='content-true'>".
                                 "<div><h4>".$articles[$x]['headline']."</h4></div>".
                                 "<div>".$articles[$x]['score']."</div>".
                                 "<div>".$urls[$x]."</div>".
                               "</div>".
                             "</div>".
                             "<div class='col-xs-4'>".
                               "<div class='content-false'>".
                                 "<div><h4>".$articles[$x+1]['headline']."</h4></div>".
                                 "<div>".$articles[$x+1]['score']."</div>".
                                 "<div>".$urls[$x+1]."</div>".
                               "</div>".
                             "</div>".
                           "</div>".
                         "</div>";

                        echo $statement;
                      }
                      ?>

                  <!--Nikhil. Just echo php statements here.-->

                    </div><!--//section-inner-->
                </section><!--//section-->
            </div><!--//primary-->


            <!--Specify company here-->
            <div class="secondary col-md-3 col-sm-12 col-xs-12">
                 <aside class="info aside section">
                    <div class="section-inner">
                        <h2 class="heading sr-only">Basic Information</h2>
                        <div class="content">
                            <ul class="list-unstyled">
                                <li><i class="fa fa-map-marker"></i><span class="sr-only">Location:</span>IIT Bhubaneswar</li>
                                <li><i class="fa fa-envelope-o"></i><span class="sr-only">Email:</span><a href="#">nikhilmolangur@gmail.com</a></li>
                                <li><i class="fa fa-link"></i><span class="sr-only">Website:</span><a href="#">https://github.com/nikhm</a></li>
                            </ul>
                        </div><!--//content-->
                    </div><!--//section-inner-->
                </aside><!--//aside-->
            </div><!--//secondary-->


            <div class="secondary col-md-3 col-sm-12 col-xs-12">
                 <aside class="info aside section">
                    <div class="section-inner">
                        <h2 class="heading sr-only">Basic Information</h2>
                        <div class="content">
                               <h4>News articles polarity</h4>
                               <b>Sentiment polarity</b> of news headline is estimated by <b>Bi-directional LSTM with attention layer</b>
                               trained on data obtained from <a href="http://alt.qcri.org/semeval2017/task5/">Semeval Task 5</a>
                        </div><!--//content-->
                    </div><!--//section-inner-->
                </aside><!--//aside-->
            </div><!--//secondary-->



          <!-- Specify company here-->
          <div class="secondary col-md-3 col-sm-12 col-xs-12">
               <aside class="info aside section">
                  <div class="section-inner">
                      <h2 class="heading sr-only">Basic Information</h2>
                      <div class="content">
                        <h4>Content Extraction</h4>
                        <b>HTML Content Extraction</b> of the source of article is done by <b>Random Forest Classifier</b> trained with data
                        obtained from <a href="http://www.l3s.de/~kohlschuetter/boilerplate/">Kohlschutter et al.</a>
                      </div><!--//content-->
                  </div><!--//section-inner-->
              </aside><!--//aside-->
          </div><!--//secondary-->




        </div><!--//row-->
    </div><!--//masonry-->

    <!-- ******FOOTER****** -->
    <footer class="footer">
        <div class="container text-center">
                <small class="copyright">Thanking <a href="http://themes.3rdwavemedia.com" target="_blank">3rd Wave Media</a> for the template</small><br/>
                <small class="copyright">This project is for academic  purposes only</small>
        </div><!--//container-->
    </footer><!--//footer-->

    <!-- Javascript -->
    <script type="text/javascript" src="assets/plugins/jquery-1.11.1.min.js"></script>
    <script type="text/javascript" src="assets/plugins/jquery-migrate-1.2.1.min.js"></script>
    <script type="text/javascript" src="assets/plugins/bootstrap/js/bootstrap.min.js"></script>
    <script type="text/javascript" src="assets/plugins/jquery-rss/dist/jquery.rss.min.js"></script>
    <!-- github activity plugin -->
    <script type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/mustache.js/0.7.2/mustache.min.js"></script>
    <script type="text/javascript" src="http://caseyscarborough.github.io/github-activity/github-activity-0.1.0.min.js"></script>
    <!-- custom js -->
    <script type="text/javascript" src="assets/js/main.js"></script>
</body>
</html>
