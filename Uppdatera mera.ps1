cd "C:\dev\tidslinje"

# 1. Hämta senaste
git pull origin main

# 2. Läs version
if (Test-Path "version.txt") {
    $version = Get-Content "version.txt"
} else {
    $version = "1.0.0"
}

# 3. Splitta version (X.Y.Z)
$parts = $version -split "\."
$major = [int]$parts[0]
$minor = [int]$parts[1]
$patch = [int]$parts[2]

# 4. Välj typ av ändring
Write-Host "Typ av ändring?"
Write-Host "1 = patch (bugfix)"
Write-Host "2 = minor (ny feature)"
Write-Host "3 = major (stor ändring)"
$choice = Read-Host "Val (1/2/3)"

if ($choice -eq "1") {
    $patch++
}
elseif ($choice -eq "2") {
    $minor++
    $patch = 0
}
elseif ($choice -eq "3") {
    $major++
    $minor = 0
    $patch = 0
}

# 5. Ny version
$newVersion = "$major.$minor.$patch"

# 6. Skriv kommentar
$comment = Read-Host "Vad ändrade du?"

# 7. Spara version
$newVersion | Out-File -Encoding ascii version.txt

# 8. Commit + push
git add .
git commit -m "v$newVersion - $comment"
git push

# 9. Status
git status
git log --oneline -n 1

# 10. Bygg
npm run build:gh
npm run deploy