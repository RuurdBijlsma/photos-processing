$dock_id = podman run --rm `
    -e POSTGRES_PASSWORD=flyingsquirrel `
    -e POSTGRES_DB=photos `
    -p 5432:5432 `
    -v data:/var/lib/postgresql/data `
    -d postgres

Write-Host -NoNewLine 'Press any key to clean up env...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

docker stop $dock_id