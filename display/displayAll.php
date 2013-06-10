<?php


print "<table><tr><td>Click this button to go on the mainPage</td><td><form action='display.php'><input type='submit' value='Back'></form></td></tr></table>";
$db = new SQLite3('db/monitor.db');
$results = $db->query('SELECT * from rpi');

$row = array();
$i=0;

while ($res = $results->fetchArray(SQLITE3_ASSOC)){
	$rowIP[$i] = $res['piIP'];
	$rowID[$i] = $res['piID']; 
	$rowCPU[$i]= $res['piCPULoad'];
	$i++;
}

print "	<table border='1'>
	<tr><td> n. </td><td> piIP </td><td> piID </td><td> piCPULoad </td></tr>";
for($i=0;$i<sizeof($rowIP);$i++){
	print "<tr><td> ".($i+1)." </td> <td> ".$rowIP[$i]."</td><td>".$rowID[$i]."</td><td>".$rowCPU[$i]."</td></tr>";
}
print "</table>";

?>
