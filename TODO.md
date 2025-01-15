## TODO

* Python
    * add more tests
    * fix mypy
    * tags column toevoegen die voor full text search gebruikt wordt. Tag ideeen
      * ultrawide
      * portrait
      * vertical
      * square
      * thinkg of more
    * gainmap photo
    * Tags voor search toevoegen: ultrawide, vertical, square, bedenk meer
    * Low quality/blurry detector
    * Do something with pipelines (logging, capture running times, show in ui)
    * dont use pytz anymore
    * when clustering (faces and images), should i really consider different frames as new points?
        * a cluster is easily made this way from just one video.
    * fix logspam
    * add integration test
    * make base clusterer for consistency
    * face embedding new points support (dont just recluster for every new photo)
    * add tests for classification
    * rename visualinformationmodel to somethling like FrameInfoModel or FrameModel
    * is panorama, is selfie, is night sight, etc. is all not being set yet.
    * Cluster images!
        * werkt best leuk, ik krijg allemaal poekie images
        * (ask llm to make album title based on many 2-3 word descriptions of images)
            * give more info than that^
                * locations (countries/cities)
                * duration of from start to end of album (weekend/year/day)
                * names of people in photos (unique faces labels)
                * start and end date of photos
    * PIL heeft exif_transpose, dit ga ik waarschijnlijk ook nodig hebben
    * periodically recluster faces
    * allow user to change cluster params, then rerun clustering
    * check if watchdog works
    * use nginx for image hosting instead of fastapi endpoints
    * add table: failed images, so it doesn't try to process them again?
    * add button [optimize library], to convert all source images to full size avif, and all videos to vp9 codec (av1 in
      the future?) (video is less important it's already h265)
    * make .env file for user to set base photos dir? set it in ui?
    * Get exiftool and ffmpeg binaries automatically?
        * put it in dockerfile
* Add albums
    * very important
    * Shared albums between servers (shared secret to access other server's album)
* For videos process a frame every fifth of the video or something.
    * when searching seek to the part of the video where it first appears
* Search photos
    * hybrid search op embedding + heel veel text fields in full text search
    * search by location (from reverse geocode)
    * search by date/time
    * how much filtering do i want? I have a lotta tags
* make android app before frontend?
* Create frontend
    * hosted on github pages?
    * Photos grid front page (infinite scroll, fitting layout, scroll to date)
    * Search bar
    * Upload from frontend
    * material theme color based on background? very pastellig
    * Map page with photos
    * Vue compnoent voor perfecte gallery
        * carousel optioneel laten zien onderin van alle fotos
        * infinite scroll support
    * Vue component voor de perfecte image viewer
        * support photo video
        * zoomen (muis en touch)
        * panoramas/360 photos in three.js laten zien
        * hdr gainmap zit in de originele jpg, niet in generated thumbnails, laat zien in app/website?
        * motion photo laten zien
            * fetch blob, slice motion video mp4 eruit, laat die zien, als ie klaar is, laat foto zien
    * admin settings (frontend)
        * photos_dir
            * photos-dir/user_id/PIC.jpg
        * thumbnails_dir
        * multithreaded_processing
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
* stuur notificaties (maak generieke notificatie systeem, web push, android notificatie)
    * notificatie voor "on this day 8 years ago" soms
    * notificatie voor random gemaakt album op basis van image clustering
    * notificatie voor "on this day 8 years ago was de eerste foto van dit album" om te zien dat je op vakantie ging op
      deze dag
* Album titel generate met llm? op basis van captions, locations/countries
* Iets van auto album generatie op basis van locatie, als je een foto maakt als je thuis bent na 10+ foto's en 2+ dagen
  niet thuis, vraag of er een album van moet komen.
    * gokken waar thuis is op basis van foto lokaties, maar ook user vragen
* Automatische album selectie van goeie fotos?
* Voor map view, heat map als je uitgezoomd bent, stipjes voor foto's waar je op kan klikken als je meer inzoomt
* Photo editor?
    * depth estimation -> blur bg?
    * depth estimation -> smart cropping?
    * image->image upscaler?
    * stable diffusion inpainting?

album title creation prompt (make sure given example input in prompt matches input structure):
also use for unprompted collection generation.

```
You are an expert in summarizing photo albums. Using the provided data, create a concise, engaging, and specific title for the album. Incorporate key details such as the primary locations, significant individuals, the date range, recurring themes, and the general mood of the album. The title should feel personal and reflective of the album's content.

Input Data:

    {input_json like in ex. below}

Output Requirements:

    Create a single descriptive title no longer than 15 words.
    Ensure the title reflects the essence of the album using the data provided.

Example Input:

{
  "people": [
    {"name": "Alice", "photo_count": 15},
    {"name": "Bob", "photo_count": 6}
  ],
  "locations": [
    {"country": "France", "city": "Paris", "photo_count": 10},
    {"country": "Italy", "city": "Rome", "photo_count": 5}
  ],
  "daterange": {
    "from": "2023-06-10",
    "to": "2023-06-20"
  },
  "photos": [
    {"caption": "Eiffel Tower at sunset", "date": "2023-06-10", "time": "18:30", "type": "image"},
    {"caption": "Colosseum during the day", "date": "2023-06-15", "time": "14:00", "type": "image"}
  ]
}

Example Output:
"Exploring Paris and Rome: Alice and Bob’s Summer Journey (June 2023)"

```