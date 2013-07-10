<?php

function hu_plugin_handler(){
    // Manually parse the URL request
    if(empty($_SERVER['REQUEST_URI'])){
        return;    // nothing to parse
    }
    
    $urlvars = explode('/', $_SERVER['REQUEST_URI']);
    
    if (count($urlvars) < 2){
        return; // nothing to parse
    }
    
    // Check for querystring variables
    // e.g.  http://my_wordpress_app.harvard.edu/hu-authz-login/....
    if(!empty($urlvars[1])){
        if($urlvars[1] == 'hu-authz-login'){
            // Redirect to custom plugin template for "item" view
            add_action('template_redirect', 'my_custom_item_template');
        }
    }
}
add_action('parse_request', 'hu_plugin_handler');

//http://gabrielharper.com/blog/2012/09/wordpress-custom-urls-for-plugins/
?>
