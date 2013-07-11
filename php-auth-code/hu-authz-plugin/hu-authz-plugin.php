<?php
/*
Plugin Name: Harvard AuthZProxy Authentication for Wordpress
Plugin URI:
Description: Creates a plugin that utilizes Harvard's AuthZProxy service when requested with the custom attributes of mail (email), sn (last name) and givenname (first name)
Version: 1.0
Author: Raman Prasad
Author URI: http://www.mcb.harvard.edu
License: GPLv2
*/

register_activation_hook( __FILE__, 'hu_authz_set_default_options' );

function hu_authz_set_default_options() {
    if ( get_option( 'hu_authz_GPG_DIR' ) === false ) {
        add_option( 'hu_authz_GPG_DIR', "home/r/username/.gnupg" );
    }
    if ( get_option( 'hu_authz_PIN_APP_NAME' ) === false ) {
        add_option( 'hu_authz_PIN_APP_NAME', "FAS_FCOR_DEPT_APP" );
    }
    if ( get_option( 'hu_authz_CHECK_PIN_IP_VALUE' ) === false ) {
        add_option( 'hu_authz_CHECK_PIN_IP_VALUE', 'false' );
    }
    if ( get_option( 'hu_authz_PRINT_DEBUG_STATMENTS' ) === false ) {
        add_option( 'hu_authz_PRINT_DEBUG_STATMENTS', 'false' );
    }

} // end "hu_authz_set_default_options"

?>