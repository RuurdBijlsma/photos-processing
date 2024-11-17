$url = "https://github.com/tensorchord/pgvecto.rs/releases/download/v0.3.0/vectors-pg17_0.3.0_amd64_public.deb"
$pgFolder = "postgres"
$destinationPath = Join-Path -Path $pgFolder -ChildPath (Split-Path -Leaf $url)

if (!(Test-Path $destinationPath))
{
    Invoke-WebRequest -Uri $url -OutFile $destinationPath
}


podman build $pgFolder -t pg-vector -f $pgFolder/Dockerfile
podman run --rm `
    -e POSTGRES_USER=postgres `
    -e POSTGRES_PASSWORD=flyingsquirrel `
    -e POSTGRES_DB=photos `
    -p 5432:5432 `
    -v pvd:/var/lib/postgresql/data `
    pg-vector