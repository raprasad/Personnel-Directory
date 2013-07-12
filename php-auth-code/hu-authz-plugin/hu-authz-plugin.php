<?php
/*
Plugin Name: Harvard AuthZProxy Authentication for Wordpress
Plugin URI:
Description: Creates a plugin that utilizes Harvard's AuthZProxy service when requested with the custom attributes of mail (email), sn (last name) and givenname (first name)
Version: 1.1
Author: Raman Prasad
Author URI: http://www.mcb.harvard.edu
License: GPLv2
*/
require_once('authz_checker.php');  // home of the AuthZChecker class

/* test urls

https://mcbintranet.unix.fas.harvard.edu/wp-content/plugins/hu-authz-plugin/hu-authz-plugin.php

https://mcbintranet.unix.fas.harvard.edu/wp-login.php?_azp_token=-----BEGIN+PGP+MESSAGE-----%0A++++Version%3A+GnuPG+v1.4.10+%28GNU%2FLinux%29%0A%0A++++hQEMA2DXKM0Yr%2BmKAQf%2BP7cfudt%2Bd9QomgN9%2BBgQDjS5U8tljS7NPjUPUM1bc3CP%0A++++OhMa2g5HKRxc6NQgkpV2BGAiMrYYLMg6MKT%2FHTUCTxeymAtGnNg15q0KzsXDAbcf%0A++++j%2B1hx9cx4JiYmV2B5sht%2Fhf277RNXj2Bmt5ugdE5HXlwohugaW0HcHNqnZ2yzkv8%0A++++Nskz96G81u1hvGvchPTgTmyY1KgDaZz%2FJq4hAxO3JqXl8Hrr5EWb7JSy%2F471QDAV%0A++++gBSNQrrws%2BHRmXVj0XQwpqwAesuyIIKVqaEDZ38MSWldtl%2BncQiBVX01URTx1suG%0A++++oWdopXa21l8TV8ZZx2Znsr1S1evmgrmG99Q6pMjNitLAAwFiFCU4Pz1DItZXVudx%0A++++1XzNfXglVgWex7CGlTnE7L%2BWj2HIGx1hsZpjJxIQKZzNwDgBtGNen25yCqGwGlkV%0A++++5shNPxjGl4MnlhXm%2BL%2FkFolQXtcDbi9KL5NqHfkTUU3fSVfKLkFWlR29qTzokaBn%0A++++5W1FlzPesyUAl5ZJ1Zv4hJDrWCYqNPgB0y9S8RiuUN7MDS1lGJc6juTYjbOrVHJz%0A++++tagqrzaD260BuYOUETjyGBrzwCscq0m3Bt90mlQwPP4VRCjR8A%3D%3D%0A++++%3D%2B9V8%0A++++-----END+PGP+MESSAGE-----%0A++++



*/

register_activation_hook( __FILE__, 'hu_authz_set_default_options_array' );

//add_filter( 'authenticate', 'hu_pin2_authz_check', 10, 3 );
add_action('init', 'hu_pin2_authz_check');


function hu_authz_set_default_options_array() {
    
    if ( get_option( 'hu_authz_options' ) === false ) {
        $authz_options_array = array(            
                'GPG_DIR' => "/home/p/r/prasad/.gnupg",
                'PIN_APP_NAME' => "FAS_FCOR_MCB_GRDB_AUTHZ",
                'CHECK_PIN_IP_VALUE' => 'false',
                'PRINT_DEBUG_STATMENTS' => 'false'
        );

        add_option('hu_authz_options', $authz_options_array );
        
    } else {
        // Use for future updates
        
         $authz_options_array = array(            
                    'GPG_DIR' => "/home/p/r/prasad/.gnupg",
                    'PIN_APP_NAME' => "FAS_FCOR_MCB_GRDB_AUTHZ",
                    'CHECK_PIN_IP_VALUE' => 'false',
                    'PRINT_DEBUG_STATMENTS' => 'false'
            );

          update_option('hu_authz_options', $authz_options_array );
    }
}

function show_fail_message($err_msg){
    print '<div style="border:2px solid #ff0000;margin:20px; padding:20px; width:400px;"><b>PIN Login Failed</b><p>'. $err_msg . '</p></div>';
    
}

/* -------------------------------------------------------------------
    Using the first name, last name, and email from the AuthZProxy Login:
        - Retrieve the user--or create a new one
        - Log the user in
        - Redirect to the front page
------------------------------------------------------------------- */
function login_wp_user_from_hu_authz($wp_user_data){

    // (1) Attempt to retrieve the user from the database
    $wp_user = get_user_by( 'login', $wp_user_data['user_login'] ); 
    
    // (2) Failed, user is not in Wordpress, create the user!
    if ($wp_user === false){
        
        // Setup the minimum required user information 
    	$wp_user_data["user_registered"] = date("Y-m-d H:i:s");     // Add a registration date/time

    	// Add the user
    	$new_user_id = wp_insert_user( $wp_user_data ); // A new user has been created
        
        // Retrieve the user
        $wp_user = get_user_by( 'id', $new_user_id );
        
        // !! Really failed, could not make the user
        if ($wp_user===false){
            show_fail_message('Sorry!  Failed to create user!');
            return;
            
        }
    }
    
    // (3) Create new user password
    $onetime_password = wp_generate_password($len=20);      // onetime password, 20 chars long
    //print "<p>onetime_password: $onetime_password ";

    // (4) Set the new password
    wp_update_user( array ( 'ID' => $wp_user->ID, 'user_pass' => $onetime_password ) ) ;

    // (5) Delete the user credentials (possible extra step but want to avoid caching)
    wp_cache_delete($existing_user->ID, 'users');
    print "<p>wp_cache_delete";
    
    // (6) Re-retrieve user with newly set password
    $wp_user = get_user_by( 'login', $wp_user_data['user_login']);  
    print '<p>next line?';

    // (7) Log the user in with the new password
    $creds = array();
    $creds['user_login'] = $wp_user->user_login;
    $creds['user_password'] = $onetime_password;
    $creds['remember'] = true;

    $logged_in_user = wp_signon( $creds, false );
    if ( is_wp_error($logged_in_user) ){
        print $logged_in_user->get_error_message();
        print 'Login failed';
        return;
    }

    wp_safe_redirect('https://mcbintranet.unix.fas.harvard.edu');
    
} // login_wp_user_from_hu_authz




function hu_pin2_authz_check(){
    
    
    // (1) If we're not on the login page, then leave
    if(!(in_array($GLOBALS['pagenow'], array('wp-login.php')))){
        return;
    }

    // (2) If there's no AuthZProxy "_azp_token" in the url, then leave
    if(!(isset($_GET['_azp_token']))){
        return;
    }
    
    // (3) Set options manually or pull them from the database
    
    // manual setting of AuthZ options
    $authz_options_array = array(
             "GPG_DIR" => '/home/p/r/prasad/.gnupg',
             "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
             "CHECK_PIN_IP_VALUE" => 'false',
             "PRINT_DEBUG_STATMENTS" => 'true'         );
        
    $authz_options_array = get_option('hu_authz_options');
    
    // Run the checker with a test array that contains a key named "_azp_token" and a full AuthZProxy message
    //$authz_checker = new AuthZChecker($TEST_GET_ARRAY, $authz_options_array);
    
    // Use the GET string, the AuthZChecker processes the url value indicated by the key "_azp_token"
    $authz_checker = new AuthZChecker($_GET, $authz_options_array);

    /* --------------------------------
        START: temporarily skipping the authz error check, using a test url
     -------------------------------- */
    
    // Pull the user information from the AuthZ checker
    $wp_user_data = $authz_checker->get_wp_user_data_array_direct();
    if ($wp_user_data == null){
        show_fail_message('Sorry!  Failed to retrieve the user data from the Pin Login!');
        return;
    }
    
    // Log in with the $wp_user_data
    login_wp_user_from_hu_authz($wp_user_data);
    return;
    /* --------------------------------
      END: temp
    -------------------------------- */
      
    //
    // If there's an authentication error, then fail and return an error message
   if ($authz_checker->has_err()== true){
       print '<div style="width:400px;border:2px solid #ff0000;margin:20px; padding:20px"><b>PIN Login Failed</b><p>';
       
        print  $authz_checker->get_error_msg_html();
        print '</p></div>';
        return;
    }
    
    // Pull the user information from the AuthZ checker
    $wp_user_data = $authz_checker->get_wp_user_data_array_safe();
    if ($wp_user_data == null){
        show_fail_message('Sorry!  Failed to retrieve the user data from the Pin Login!');
        return;
    }
    
    // Log in with the $wp_user_data
    login_wp_user_from_hu_authz($wp_user_data);

}  // end hu_pin2_authz_check

?>