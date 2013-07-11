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
/*
function GET_login() {
    //Check that we are on the log-in page
    if(in_array($GLOBALS['pagenow'], array('wp-login.php'))):

    //Check that log and pwd are set
        if(isset($_GET['log']) && isset($_GET['pwd'])):
            $creds = array();
            $creds['user_login'] = $_GET['log'];
            $creds['user_password'] = $_GET['pwd'];
            $creds['remember'] = true; //Do you want the log-in details to be remembered?

            //Where do we go after log-in?
            $redirect_to = admin_url('profile.php');

            //Try logging in
            $user = wp_signon( $creds, false );

            if ( is_wp_error($user) ){
                //Log-in failed
            }else{
                //Logged in, now redirect
                $redirect_to = admin_url('profile.php');
                wp_safe_redirect($redirect_to);
            exit();
            }
        endif;
    endif;
    //If we are not on the log-in page or credentials are not set, carry on as normal
}
*/


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
        
        
        //$authz_options_array = get_option('hu_authz_options');
        //$authz_options_array['PRINT_DEBUG_STATMENTS'] = 'false';
        //update_option( 'hu_authz_options', $authz_options_array );
        //if ( $existing_options['version'] < 1.1 ) {
        //    $existing_options['track_outgoing_links'] = false;
        //    $existing_options['version'] = "1.1";
        //    update_option( 'hu_authz_options', $authz_options_array );
        //}
    }
}


function get_wp_user_from_hu_authz($wp_user_data){

    $userobj = new WP_User();
    
    // Attempt to retrieve the user from the database
    $user = $userobj->get_data_by( 'email', $wp_user_data['user_email'] ); // Does not return a WP_User object <img src='http://ben.lobaugh.net/blog/wp-includes/images/smilies/icon_sad.gif' alt=':(' class='wp-smiley' />

    // Attempt to load up the user with that ID
    $wp_user = new WP_User($user->ID); 
 
    if( $user->ID == 0 ) {
	    // The user does not currently exist in the WordPress user table.
	    // You have arrived at a fork in the road, choose your destiny wisely
	     
	    // If you do not want to add new users to WordPress if they do not
	    // already exist uncomment the following line and remove the user creation code
	    //$user = new WP_Error( 'denied', __("<strong>ERROR</strong>: Not a valid user for this system") );
	     
	    // Setup the minimum required user information 
	    $wp_user_data["user_registered"] = date("Y-m-d H:i:s");
	    
	    $new_user_id = wp_insert_user( $wp_user_data ); // A new user has been created
 
	    // Load the new user info
	    $wp_user = new WP_User($new_user_id);
    }// end make new user
    
//    $password = 'HelloWorld';
 //   wp_set_password( $password, $user_id );
    
  //  $user = wp_signon( $creds, false );

    return $wp_user;
    
}




function hu_pin2_authz_check(){
    
    
    //Check that we are on the log-in page
    if(!(in_array($GLOBALS['pagenow'], array('wp-login.php')))){
        return;
    }
    
    if(!(isset($_GET['_azp_token']))){
        return;
    }
        
    //$test_authz_params = array(
    //         "GPG_DIR" => '/home/p/r/prasad/.gnupg',
    //         "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
    //         "CHECK_PIN_IP_VALUE" => false,
    //         "PRINT_DEBUG_STATMENTS" => true         );
        
    $authz_options_array = get_option('hu_authz_options');
    
        
    //$authz_checker = new AuthZChecker($TEST_GET_ARRAY, $authz_options_array);
    $authz_checker = new AuthZChecker($_GET, $authz_options_array);


    // If there's an authentication error, then fail and return an error message
   
   /* if ($authz_checker->has_err()== true){
        print_r($authz_options_array);
        
        print "<p>$authz_checker->encrypted_azp_token</p>";
        
        
        print  $authz_checker->get_error_msg_html();
        exit;
        $user_err_msg = "<strong>ERROR</strong>: " . $authz_checker->get_error_msg_html();
	    $user = new WP_Error( 'denied', __($user_err_msg) );
        return $user;
    }
    */
    
    $wp_user_data = $authz_checker->get_wp_user_data_array();
   // print_r($wp_user_data);
//    print 'blah';
    //exit;
    // Comment this line if you wish to fall back on WordPress authentication
    // Useful for times when the external service is offline
    //remove_action('authenticate', 'wp_authenticate_username_password', 20);ff
    
    
    return get_wp_user_from_hu_authz($wp_user_data);

}  // end hu_pin2_authz_check

?>