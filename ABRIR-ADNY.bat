@echo off
setlocal
cd /d "%~dp0"
if exist "ADNY-DTF-Halftone.exe" goto abrir
echo Baixando o aplicativo ADNY para Windows. Aguarde...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; $base='https://github.com/adnyestampa-dot/ADNY-DTF-Halftone/releases/latest/download/'; $nome='ADNY-DTF-Halftone.exe'; $destino=Join-Path (Get-Location) $nome; $parcial=$destino+'.part'; $hashfile=$parcial+'.sha256'; try { Invoke-WebRequest -UseBasicParsing -Uri ($base+$nome) -OutFile $parcial; Invoke-WebRequest -UseBasicParsing -Uri ($base+$nome+'.sha256') -OutFile $hashfile; $esperado=((Get-Content -Raw -LiteralPath $hashfile).Trim() -split '\s+')[0]; if ($esperado -notmatch '^[a-fA-F0-9]{64}$') { throw 'Hash de verificacao invalido' }; $stream=[IO.File]::OpenRead($parcial); $alg=[Security.Cryptography.SHA256]::Create(); try { $recebido=[BitConverter]::ToString($alg.ComputeHash($stream)).Replace('-','').ToLowerInvariant() } finally { $stream.Dispose(); $alg.Dispose() }; if ($recebido -ne $esperado) { throw 'O arquivo recebido nao passou na verificacao SHA256' }; Move-Item -LiteralPath $parcial -Destination $destino -Force; Remove-Item -LiteralPath $hashfile -Force } catch { if (Test-Path -LiteralPath $parcial) { Remove-Item -LiteralPath $parcial -Force }; if (Test-Path -LiteralPath $hashfile) { Remove-Item -LiteralPath $hashfile -Force }; Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 (
  echo Nao foi possivel baixar o aplicativo. Confira a conexao e tente novamente.
  pause
  exit /b 1
)
:abrir
start "" "%~dp0ADNY-DTF-Halftone.exe" %*
exit /b 0
