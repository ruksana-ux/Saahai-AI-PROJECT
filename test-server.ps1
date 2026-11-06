$port = 5500
$prefix = "http://localhost:$port/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)

try {
    $listener.Start()
    Write-Output "Sahaaya AI server listening at $prefix"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $relPath = $request.Url.LocalPath.TrimStart('/')
        if ([string]::IsNullOrEmpty($relPath)) {
            $relPath = 'index.html'
        }

        $filePath = Join-Path $PSScriptRoot $relPath

        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            
            if ($ext -eq '.html') {
                $response.ContentType = 'text/html; charset=utf-8'
            } elseif ($ext -eq '.css') {
                $response.ContentType = 'text/css; charset=utf-8'
            } elseif ($ext -eq '.js') {
                $response.ContentType = 'application/javascript; charset=utf-8'
            } elseif ($ext -eq '.json') {
                $response.ContentType = 'application/json; charset=utf-8'
            } elseif ($ext -eq '.svg') {
                $response.ContentType = 'image/svg+xml'
            } else {
                $response.ContentType = 'application/octet-stream'
            }

            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes('404 Not Found')
            $response.OutputStream.Write($msg, 0, $msg.Length)
        }
        $response.Close()
    }
}
catch {
    Write-Error $_
}
finally {
    $listener.Stop()
    $listener.Close()
}
