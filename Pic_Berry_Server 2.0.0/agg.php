<?php

    $comando = $_POST["comando"];
    $device = $_POST["device"];
    //$comando = $_GET["comando"];
    //$device = $_GET["device"];  
    
    if ($comando=="aggiorna" && $device == "tutti")
    {            
        $msg = "aggiorna";        
        $buf= "aggiorna";
        
        //echo $risp;
        //$soc_data = socket_set_options($sock, SOL_SOCKET, SO_BROADCAST, 1); //Set
       
        //echo $soc_data;
         
    }
    else
    {        
        $msg = "BOOO";
        //$len = strlen($stringa);
        $buf= " spedisco questo";
    }
    $host = "127.0.0.1";
    $port = "9999";
    $timeout = 15;  //timeout in seconds
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)
         or die("Unable to create socket\n");
    socket_set_nonblock($socket)
        or die("Unable to set nonblock on socket\n");
    $time = time();
    $risp = socket_connect($socket, $host, $port);
    $sock_data = socket_send($socket, $msg, strlen($msg),0); //Send data
    $soc_data = socket_recv($socket, $buf , strlen($buf),0);
    echo "$sock_data\n";
    echo $buf;
    socket_close($socket);        
    //echo "aggiornato";
    
?>