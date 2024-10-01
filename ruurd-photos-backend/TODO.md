## TODO

* Python
  * add tests
  * logs not showing in docker compose?
  * env files for different environments
  * use nginx for image hosting instead of fastapi endpoints
  * ci/cd?
  * create docker/docker compose configs
* Add users
  * roles (server admin/user)
* Add albums
  * Shared albums between servers (oauth2 for auth)
* Add exif processing
  * time taken + timezone
  * location + reverse geocode
  * capture info (iso, etc.)
  * ...
* Add ai processing
  * image caption (text and embedding)
    * Cluster on caption embeddings? kmeans op embeddings
    * pca to reduce dimensionality of embeddings? for speed
    * periodically run algorithm to determine amount of clusters (elbow method)
  * image object detection (list of objects in image?)
  * facial recognition (group by faces)
  * detect document -> OCR
  * For videos process a frame every fifth of the video or something.
* Search photos
  * Semantic search (caption, object, ocr text)
  * postgres full text search
  * search by location (from reverse geocode)
  * search by date/time
* Add albums
  * Shared albums (with other servers)
* Create frontend
  * hosted on github pages?
  * Photos grid front page (infinite scroll, fitting layout, scroll to date)
  * Search bar
  * Upload from frontend
  * Map page with photos
  * Explore page
    * Locations (cities/countries)
    * Things
    * Persons (from face recognition)
    * Categories
      * videos
      * photos
      * panorama
      * screenshots
      * preset search queries (sunset, food, cats, dogs, selfie)
  * Server admin panel
    * Create/remove user on server (with storage limit?)
  * System info
    * storage left
    * resource usage (cpu,ram,etc)
    * media processing info
* Create android gallery app with local and cloud photos