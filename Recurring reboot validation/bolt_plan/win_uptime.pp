#This plan executes a script to fetch uptime of windows server
plan ntt_monitoring::win_uptime(TargetSpec $targets)
{
	run_plan('ntt_monitoring::st2kv_env', $targets)
	$system_uptime = run_task('ntt_monitoring::win_uptime', $targets)
	$output_data = $system_uptime.first().value['_output']
	$result = {'output' => $output_data}
	return $result
}
