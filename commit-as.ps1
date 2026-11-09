# Helper script to commit as different collaborators
# Usage: .\commit-as.ps1 <person> "<commit message>"
# Example: .\commit-as.ps1 me "Add new feature"
# Example: .\commit-as.ps1 bscc "Update documentation"
# Example: .\commit-as.ps1 shadreck "Fix bug in API"

param(
    [Parameter(Mandatory=$true)]
    [string]$Person,
    
    [Parameter(Mandatory=$true)]
    [string]$Message
)

switch ($Person.ToLower()) {
    "me" {
        $author = "funke55 <bsc-inf-22-21@unima.ac.mw>"
    }
    "bscc" {
        $author = "bscc-com-24-23 <bscc-email@example.com>"
    }
    "shadreck" {
        $author = "Shadreck Mhandawire <shadreck-email@example.com>"
    }
    default {
        Write-Host "Unknown person. Use: me, bscc, or shadreck"
        exit 1
    }
}

Write-Host "Committing as: $author"
git commit --author="$author" -m "$Message"
