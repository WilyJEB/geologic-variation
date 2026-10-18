$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$target = Join-Path $root 'libs/terrain-diffusion-standalone.jar'
$expected = '2dde446332d4d219f7558116081830c4670ae615484268ee1734b01b1a85ea19d85b5d455828fd27fea0657f2bfad7f3c8f1b873179b206a56958804516e7453'
if (Test-Path -LiteralPath $target) {
    if ((Get-FileHash $target -Algorithm SHA512).Hash.ToLowerInvariant() -eq $expected) { Write-Output 'Pinned dependency verified.'; exit 0 }
    throw 'Existing dependency has an unexpected hash. Move it aside before retrying.'
}
New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
Invoke-WebRequest 'https://github.com/xandergos/terrain-diffusion-mc/releases/download/2.3.0-preview/NeoForge-terrain-diffusion-mc-2.3.0-windows%2B1.21.1.jar' -OutFile "$target.download"
if ((Get-FileHash "$target.download" -Algorithm SHA512).Hash.ToLowerInvariant() -ne $expected) { throw 'Downloaded dependency hash mismatch.' }
Move-Item -LiteralPath "$target.download" -Destination $target
Write-Output 'Pinned dependency downloaded and verified.'
