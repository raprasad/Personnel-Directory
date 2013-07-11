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

register_activation_hook( __FILE__, 'hu_authz_set_default_options_array' );

add_filter( 'authenticate', 'hu_pin2_authz_check', 10, 3 );

$HU_AUTHZ_OPTIONS_KEY_NAME = 'hu_authz_options';


function hu_authz_set_default_options_array() {
    global $HU_AUTHZ_OPTIONS_KEY_NAME;
    
    if ( get_option( $HU_AUTHZ_OPTIONS_KEY_NAME ) === false ) {
        $authz_options_array = array(            
                'GPG_DIR' => "/home/p/r/prasad/.gnupg",
                'PIN_APP_NAME' => "FAS_FCOR_MCB_GRDB_AUTHZ",
                'CHECK_PIN_IP_VALUE' => 'false',
                'PRINT_DEBUG_STATMENTS' => 'false'
        );

        add_option($HU_AUTHZ_OPTIONS_KEY_NAME, $authz_options_array );
        
    } else {
        // Use for future updates
        $authz_options_array = get_option($HU_AUTHZ_OPTIONS_KEY_NAME);
        $authz_options_array['PRINT_DEBUG_STATMENTS'] = 'false';
        update_option( $HU_AUTHZ_OPTIONS_KEY_NAME, $authz_options_array );
        //if ( $existing_options['version'] < 1.1 ) {
        //    $existing_options['track_outgoing_links'] = false;
        //    $existing_options['version'] = "1.1";
        //    update_option( $HU_AUTHZ_OPTIONS_KEY_NAME, $authz_options_array );
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
	    $new_user_id = wp_insert_user( $wp_user_data ); // A new user has been created
 
	    // Load the new user info
	    $wp_user = new WP_User ($new_user_id);
    }// end make new user

    return $wp_user;
    
}

function hu_pin2_authz_check(){
    global $HU_AUTHZ_OPTIONS_KEY_NAME;
    
    /*$test_authz_params = array(
             "GPG_DIR" => '/home/p/r/prasad/.gnupg',
             "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
             "CHECK_PIN_IP_VALUE" => false,
             "PRINT_DEBUG_STATMENTS" => true
             
             );
    */        
    $authz_options_array = get_option($HU_AUTHZ_OPTIONS_KEY_NAME);
     
    $authz_checker = new AuthZChecker($_GET, $authz_options_array);

    // If there's an authentication error, then fail and return an error message
    if ($authz_checker->has_err()== true){
        $user_err_msg = "<strong>ERROR</strong>: " . $authz_checker->get_error_msg_html();
	    $user = new WP_Error( 'denied', __($user_err_msg) );
        return $user;
    }
    
    
    $wp_user_data = $authz_checker->get_wp_user_data_array();
    
    // Comment this line if you wish to fall back on WordPress authentication
    // Useful for times when the external service is offline
    //remove_action('authenticate', 'wp_authenticate_username_password', 20);
    
    
    return get_wp_user_from_hu_authz($wp_user_data);

}  // end hu_pin2_authz_check
?>




