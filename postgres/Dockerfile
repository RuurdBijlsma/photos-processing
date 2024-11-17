# Use the official PostgreSQL image
FROM postgres:latest

# Copy the .deb file into the container
COPY vectors-pg17_0.3.0_amd64_public.deb /tmp/vectors-pg17_0.3.0_amd64_public.deb

# Install the .deb package
RUN apt-get update && \
    apt-get install -y /tmp/vectors-pg17_0.3.0_amd64_public.deb && \
    rm -f /tmp/vectors-pg17_0.3.0_amd64_public.deb

# Add configuration commands as a script
COPY configure-postgres.sh /docker-entrypoint-initdb.d/
