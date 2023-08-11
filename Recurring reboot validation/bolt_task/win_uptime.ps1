$uptime_data = (get-ciminstance -ClassName Win32_OperatingSystem).LastBootUptime
$current_date = get-date
$uptime = $current_date - $uptime_data
write-output $uptime.TotalMinutes
