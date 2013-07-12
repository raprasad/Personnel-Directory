<?php
/* 
    Optional check to see if someone is in the MCB directory
*/

// echo json_encode(array('result' => '1', 'username' => 'bob', 'first_name' => 'Bob', 'last_name' => 'Jacobsen', 'email' => 'aaben@lobaugh.net'));

function is_email_in_mcb_directory(){

    $response = wp_remote_get( "https://www.mcb.harvard.edu/mcb/is_mcb_user?email=$email_address" );
    $ext_auth = json_decode( $response['body'], true );
    if( $ext_auth['result'] == 1 ) {
        return true;
    }
    return false;
}


?>