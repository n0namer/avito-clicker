param(
    [Parameter(Mandatory=$false)][string]$Query = "project manager",
    [Parameter(Mandatory=$false)][string]$CitySlug = "rossiya",
    [Parameter(Mandatory=$false)][string]$Url = "",
    [Parameter(Mandatory=$false)][int]$Limit = 50
)
$ErrorActionPreference = "Stop"
if ($Url) {
    python -m avito_clicker search --url $Url --limit $Limit
} else {
    python -m avito_clicker search --query $Query --city-slug $CitySlug --limit $Limit
}
