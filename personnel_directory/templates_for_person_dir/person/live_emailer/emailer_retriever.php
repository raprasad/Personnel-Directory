<?

function show_debug_lines(){
    global $query_str, $base_url, $ajax_url;
    print "<br />query_str: $query_str";
    
    print "<br />base_url: $base_url";
    print "<br />ajax_url: $ajax_url";
    print '<hr />';
    
}

/*
    Cross-site scripting doesn't work, so access the data via PHP.
*/
$query_str =  $_SERVER['QUERY_STRING'];     // with params for email search
$base_url = 'https://webapps.sciences.fas.harvard.edu/mcb/p/email-search/?';
$ajax_url = $base_url .$query_str; 

//show_debug_lines();
//$ajax_url = 'https://webapps.sciences.fas.harvard.edu/mcb/p/email-meta/';

$content = file_get_contents($ajax_url);

echo $content;

?>