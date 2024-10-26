## TODO

* processing pipeline
    1. Clean dangling db entries by deleting every database entry where there is no source image
    2. for every user in db:
        1. list files in photos dir
        2. filter supported types (video, image)
        3. find photos that aren't already completely processed, each photo must have:
            1. every size thumbnail, and each video a vid.webm
            2. an entry in the db
        4. for each photo that has to processed (may be done multithreaded):
            1. Generate basic metadata (id, path, hash)
            2. generate thumbnails+webm if needed (thumbnail folder is named after image hash, so it may already exist)
            3. generate metadata
                1. exif
                2. gps
                3. time_taken
            4. store image in database
        5. for every photo that has no UTC time yet
            1. find nearest image by datetime
            2. calculate UTC time, timezone offset, and timezone name from the location of the nearest image + the local
               datetime of the image.
           3. update in db
    3. delete thumbnails where the source image does not exist anymore

* project structure
  1. 

* Python
    * add tests
    * PIL heeft exif_transpose, dit ga ik waarschijnlijk ook nodig hebben
    * alle model capabilities even op een rijtje zetten
        * clip (dubious): image en text embeddings in zelfde embedding space
        * llama 3.2 (very good):
            * llm
            * llm met vision mogelijkheid (vision niet geprobeerd)
            * kan text embeddings maken
        * minicpm (very good): llm met vision (alleen vision geprobeerd)
        * blip image captioning (basic but works): image to text captions
        * vit-base-patch16-224 (limited classification count, but can be useful): image classification: image to 1 of
          1000 classifications
        * nvidia/segformer (looks good but cant get it to run): image segmentation, en classification per segment.
          segments are per "pixel", not bounding boxes
        * facebook/detr-resnet-50: classify multiple objects per image, boundingbox per recognzied object
        * google/owlvit-base-patch32: clip van google (niet goed onderzocht)
    * CLIP model kan image en text embeddings in zelfde space maken
        * is clip wel goed? ik krijg niet zo hoge similarity scores
        * beide proberen
    * vergelijking maken van verschillende image caption methodes:
    * compare speed, accuracy, put in table
        * blip salesforce
        * llama vision
        * question_image
    * vision llm-> ask many questions, then cluster on embeddings of answers to get collections of photos, example:
        * what type of place is this photo taken? (e.g. park, beach, city) keep you answer direct and to the point.
        * then make embedding of answer
        * with every photo having such an embedding, cluster on this column to make collections of types of places, for
          example beach collection
    * watch for photo deletion and delete from db?
    * use nginx for image hosting instead of fastapi endpoints
    * ci/cd?
    * add table: failed images, so it doesn't try to process them again?
    * add button [optimize library], to convert all images to avif, and all videos to vp9 codec (av1 in the future?)
    * make .env file for user to set base photos dir
    * Get exiftool and ffmpeg binaries automatically?
* Add albums
    * Shared albums between servers (shared secret to access other server's album)
* Add AI processing
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
* Create frontend
    * hosted on github pages?
    * Photos grid front page (infinite scroll, fitting layout, scroll to date)
    * Search bar
    * Upload from frontend
    * Map page with photos
    * hdr gainmap zit in de originele jpg, niet in generated thumbnails, laat zien in app/website?
    * vue component maken om motion photo te laten zien
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