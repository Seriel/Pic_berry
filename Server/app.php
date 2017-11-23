<?php
/*
function my_callback_function() {
    $so_data = socket_recv($socket, $buf , 13,0);
    echo 'hello world!';
    $cavolo= "123";
    return $buf;
}
*/

    $comando = $_GET["comando"];  // attenzione index.html chiama agg.php  e non questa
    $device = $_GET["device"];  
    if ($comando=="aggiorna" && $device == "tutti")
    {            
        $msg = "aggiorna";        
        $buf= "aggiorna";
        
        //echo $risp;
        //$soc_data = socket_set_options($sock, SOL_SOCKET, SO_BROADCAST, 1); //Set
       
        //echo $soc_data;
         
    }
    elseif($comando=="istantaneo" && $device == "tutti")
    {
        $msg = "istantaneo";        
        $buf= "RIVEVEREIWRTY";
        
    }
    else
    {
        
        
        
        $msg = $comando." ".$device;
        //$len = strlen($stringa);
        $buf= "RIVEVEREIWRTY";
        $msg = $comando.$device;
    }
    
    $msg = $comando." ".$device;
    $host = "127.0.0.1";
    $port = "9999";
    $timeout = 15;  //timeout in seconds
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)
         or die("Unable to create socket\n");
    socket_set_nonblock($socket)
        or die("Unable to set nonblock on socket\n");
    $time = time();
    $risp = socket_connect($socket, $host, $port);
    $sock_data = socket_send($socket, $msg, strlen($msg),0);  //Send data
    $buf= "RI";
    $i = 0;
    while ($i < 15)
    {
        $soc_data = socket_recv($socket, $buf , 40, MSG_WAITALL);
        //if (false !== ($soc_data = socket_recv($socket, $buf, 13, MSG_WAITALL))) {
        //    break;
        if ($soc_data == 40) break;
        
    sleep(1);
    $i++;
    }
    
    
    //$soc_data = socket_recv($socket, $buf , 13, MSG_WAITALL);
     
    // $buf =  call_user_func('my_callback_function');
    //echo MSG_WAITALL;
    echo "$buf\n";
    //echo "$sock_data\n";
    //echo "$soc_data\n";
    //echo "$risp\n";
    //echo "$buf\n";
    socket_close($socket);        
    //echo "aggiornato";
    
?>