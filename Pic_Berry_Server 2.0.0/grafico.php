<?php
    if ($_POST){
	/* Your Database Name */
	//$dbname = 'pic_berry';
	/* Your Database User Name and Passowrd */
	//$username = 'root';
	//$password = '';
        
	require('config.php');
        
	$data_inizio = $_POST["dataI"];
        $data_fine = $_POST["dataF"];
        $tabella =$_POST["dett"]; 
        $device =$_POST["device"];
	$cosa =$_POST["cosa"];
	$device_gg = $device.$tabella;
	$device_mm = $device.$tabella;
	$device_ii = $device.$tabella;
	
	$rows = array();
	try {
	    /* Establish the database connection */
	    $conn = new PDO("mysql:host=localhost;dbname=$dbname", $username, $password);
	    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	    if ($tabella =="det")
	    {  
		$result = $conn->query("select giorno, ora, (watt*12) FROM $device where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string)($r['giorno']." ".substr($r['ora'],0,5)),'y' => (int) $r['(watt*12)']);
		    
		}
	    }
	    
	    elseif ($tabella == "_gg")
	    {
		if ($cosa == "max5"){
		    $result = $conn->query("select giorno, (max5*12) FROM $device_gg where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		    foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string) $r['giorno'],'y' => (int) $r['(max5*12)']); 		
		    }
		}
		elseif ($cosa == "maxi"){
		    $result = $conn->query("select giorno, maxi FROM $device_gg where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		    foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string) $r['giorno'],'y' => (int) $r['maxi']); 		
		    }
		}		
		else{
		    /* select all the weekly tasks from the table googlechart */
		    $result = $conn->query("select giorno, watt FROM $device_gg where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		
		    foreach($result as $r) {
		        //$temp = array();
		        $rows[] = array('label' => (string) $r['giorno'],'y' => (int) $r['watt']); 
		    }
		}    
	    }
            elseif ($tabella == "_mm")
            {                                           // (watt*12)
		if ($cosa == "max5"){
		    $result = $conn->query("select watt_max5_data, (watt_max5*12) FROM $device_mm where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		    foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string) $r['watt_max5_data'],'y' => (int) $r['(watt_max5*12)']); 		
		    }
		}
		elseif ($cosa == "maxi"){
		    $result = $conn->query("select watt_max_data, watt_max FROM $device_mm where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		    foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string) $r['watt_max_data'],'y' => (int) $r['watt_max']); 		
		    }
		}
		else{
		    $result = $conn->query("select giorno, watt FROM $device_mm where (giorno>='$data_inizio' and giorno <= '$data_fine');");
		    foreach($result as $r) {
		        //$temp = array();
		        $rows[] = array('label' => (string) $r['giorno'],'y' => (int) $r['watt']); 
		    }
		}
	    }
	    elseif ($tabella == "_ii")
	    {
		$result = $conn->query("select ora, watt FROM $device_ii where (giorno>='$data_inizio' and giorno <='$data_fine');");
		foreach($result as $r) {
		    //$temp = array();
		    $rows[] = array('label' => (string) $r['giorno'],'y' => (int) $r['watt']); 
		}
	    }      
	   
	    mysql_close($conn);
	    $jsonRows = json_encode($rows);
	    echo $jsonRows;
	    //echo $jsonTable;
	    
	} catch(PDOException $e) {
	    echo 'ERROR: ' . $e->getMessage();
	    }
    }
?>
