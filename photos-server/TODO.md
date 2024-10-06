## TODO

* Python
    * add tests
    * als latitude en longitude 0 zijn, zet gps info naar None!
    * watch for photo deletion and delete from db?
    * use nginx for image hosting instead of fastapi endpoints
    * ci/cd?
    * after process all is done, go over list again to timezone_known=false, then give them timezone from neighbouring
      photo (closest in datetime)
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
* Album titel generate met llm? op basis van captions, locations/countries
* Iets van auto album generatie op basis van locatie, als je een foto maakt als je thuis bent na 10+ foto's en 2+ dagen niet thuis vraag of er een album van moet komen.
  * gokken waar thuis is op basis van foto lokaties, maar ook user vragen
* Automatische album selectie van goeie fotos?
* Voor map view, heat map als je uitgezoomd bent, stipjes voor foto's waar je op kan klikken als je meer inzoomt