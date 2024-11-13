## TODO

* Python
    * add tests
    * PIL heeft exif_transpose, dit ga ik waarschijnlijk ook nodig hebben
    * make pipeline models interchangable with other ones, maybe make them as a local package that has input->output
    * when processing is finished, make it into a package (everything that can be done on 1 foto at least)
      * input: image file path
      * output: everything that's in an image db row. (apart from timezone fixes and facial recognition probably)
    * pipeline models:
      * CLIP for embedding text and image
      * minicpm: ask questions for extra info about images + a text description
        * llama 3.2: ask what questions to ask to improve caption
      * multi-object classification, either:
        * nvidia/segformer (segment pixel based)
        * facebook/detr-resnet-50 (boundingbox per recognized object)
      * face detection
        1. bounding box face for every photo
        2. extract face images from each photo
        3. faces_table:
           * id (uuid).
           * face embedding
           * image_id (relation to images table)
           * also put in bounding box coords
           * unique_face_id (relation to unique faces table)
        4. face_names_table
           * unique_face_id
           * face name (user input)
           * centroid_embedding (centroid of the cluster)
        5. when a new photo is processed, find its cluster by looking at the nearest face embedding and copying that unique_face_id
        6. re-cluster all embeddings in face table after `process_all`, and weekly (to accommodate new clusters(faces))
           * calculate centroid embedding for each cluster
      * scene recognition?
      * if image has legible text, do ocr and put in db
    * model capabilities (in order of usefulness):
        * minicpm (very good): llm met vision (question images) (alleen vision geprobeerd)
        * CLIP model kan image en text embeddings in zelfde space maken
        * llama 3.2 (very good):
            * llm
            * llm met vision mogelijkheid (vision niet geprobeerd)
            * kan text embeddings maken
        * vit-base-patch16-224 (limited classification count, but can be useful): image classification: image to 1 of
          1000 classifications
        * nvidia/segformer (looks good but cant get it to run): image segmentation, en classification per segment.
          segments are per "pixel", not bounding boxes
        * facebook/detr-resnet-50: classify multiple objects per image, boundingbox per recognzied object
        * google/owlvit-base-patch32: clip van google (niet goed onderzocht)
        * blip image captioning (basic but works): image to text captions
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
      * when searching seek to the part of the video where it first appears
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