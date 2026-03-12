$iperf = ".\IPERF_2_1_8_WIN.EXE"
$server = "10.0.0.1"
# sweep values (powers of two)
$parallel_list = 2,4,8,16,32,64
$window_list   = 1KB,2KB,4KB,8KB,16KB,32KB,64KB,128KB,256KB,512KB,1MB,2MB,4MB
$length_list   = 1KB,2KB,4KB,8KB,16KB,32KB,64KB,128KB,256KB,512KB,1MB,2MB,4MB
foreach ($p in $parallel_list) {
    foreach ($w in $window_list) {
        foreach ($l in $length_list) {
            $cmd = "$iperf -c $server -P$p -w$w -l$l --sum-only -d"
            Write-Host "Running: $cmd"
            $result = & $iperf -c $server -P$p -w$w -l$l --sum-only -d
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            Add-Content -Path "iperf_results.txt" -Value "[$timestamp] $cmd"
            Add-Content -Path "iperf_results.txt" -Value $result
            Add-Content -Path "iperf_results.txt" -Value ""
        }
    }
}