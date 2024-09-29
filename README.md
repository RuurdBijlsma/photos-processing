# Ruurd Photos 2

For now very basic functionality only.

## TODO
* Python
  * add types
  * add tests
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