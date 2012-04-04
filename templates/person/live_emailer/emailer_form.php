<?
/*
    Retrieve complete HTML page with form from the webapps server and dump to this page
*/

$email_form_url = 'https://webapps.sciences.fas.harvard.edu/mcb/p/emailer-form/?json_url=emailer_retriever.php';
//header('Content-type: application/json');
$content = file_get_contents($email_form_url);
echo $content;

?>