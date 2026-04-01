# Show the installed distributions and their WSL versions.
wsl --list --verbose

# Confirm that the Virtual Machine Platform feature is enabled.
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
