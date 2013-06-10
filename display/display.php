<?php
print "Here you can:<br>1. see the data of the specific 'rpi'<br>2. view all the data in one table<br>";

$db = new SQLite3('db/monitor.db');
$results1 = $db->query('SELECT piIP from rpi group by piIP');
$row1 = array();
$i=0;

print "<br><br><table><tr> <td>rpi IP</td><td>OPTION</td></tr>";
while ($res1 = $results1->fetchArray(SQLITE3_ASSOC)){
	print"	<tr>	<td>". $res1['piIP']."</td>
			<td><form action='displaySpecific.php' method='get'><input type='hidden' name='rpiIP'  				value=".$res1['piIP']."> <input type='submit' value='ViewData' ></form></td>
		</tr>";
}
print "<tr><td></td><td><form action='displayAll.php'><input type='submit' value='ViewALL'></form></td></tr></table>";
?>
