podman run --rm `
  --name pgvectors `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=flyingsquirrel `
  -e POSTGRES_DB=photos `
  -p 5432:5432 `
  -v pgdata:/var/lib/postgresql/data `
  -d tensorchord/pgvecto-rs:pg17-v0.4.0