import json
from functools import lru_cache
from pathlib import Path

import PIL
import numpy as np
from PIL.Image import Image

from app.data.enums.activity_type import ActivityType
from app.data.enums.animal_type import AnimalType
from app.data.enums.document_type import DocumentType
from app.data.enums.event_type import EventType
from app.data.enums.object_type import ObjectType
from app.data.enums.people_type import PeopleType
from app.data.enums.scene_type import SceneType
from app.data.interfaces.visual_information import TextSummaryVisualInformation, \
    CaptionVisualInformation
from app.machine_learning.classifier.CLIPClassifier import CLIPClassifier
from app.machine_learning.embedding.CLIPEmbedder import CLIPEmbedder

classifier = CLIPClassifier()


@lru_cache
def get_scenes() -> dict[str, str]:
    scenes_path = Path(__file__).parents[2] / "assets/scenes.json"
    with open(scenes_path, 'r') as f:
        return json.load(f)


def classify_image_scene(image_embedding: np.ndarray) -> tuple[SceneType, float]:
    scenes = get_scenes()
    best_index, confidence = classifier.classify_image(
        image_embedding,
        [prompt for prompt in scenes.values()]
    )
    # confidence threshold 0.003 or something could be good
    best_label = SceneType(list(scenes.keys())[best_index])
    if confidence < 0.003:
        best_label = SceneType.UNKNOWN
    return best_label, confidence


def binary_classifications(image_embedding: np.ndarray):
    people_type: PeopleType | None = None
    animal_type: AnimalType | None = None
    document_type: DocumentType | None = None
    object_type: ObjectType | None = None
    activity_type: ActivityType | None = None
    event_type: EventType | None = None

    contains_people, _ = classifier.binary_classify_image(
        image_embedding,
        "This image contains people or a person.",
        "There are no people in this image."
    )
    if contains_people:
        best_index, _ = classifier.classify_image(image_embedding, [
            "This is a selfie where a person holds the camera, "
            "showing their face prominently.",
            "This is a group photo",
            "This is a portrait photo of a person or persons",
            "This is a crowd of people",
        ])
        people_type = [
            PeopleType.SELFIE,
            PeopleType.GROUP,
            PeopleType.PORTRAIT,
            PeopleType.CROWD,
        ][best_index]

    contains_animal, _ = classifier.binary_classify_image(
        image_embedding,
        "There is an animal or a pet, such as a cat, dog, guinea pig, "
        "rabbit, hamster, rat, bird or wildlife.",
        "There is no pet or animal here."
    )
    if contains_animal:
        best_index, _ = classifier.classify_image(image_embedding, [
            "This is a cat",
            "This is a dog",
            "This is a guinea pig",
            "This is a rabbit",
            "This is a hamster",
            "This is a rat",
            "This is bird",
            "This is wildlife",
        ])
        animal_type = [
            AnimalType.CAT,
            AnimalType.DOG,
            AnimalType.GUINEA_PIG,
            AnimalType.RABBIT,
            AnimalType.HAMSTER,
            AnimalType.RAT,
            AnimalType.BIRD,
            AnimalType.WILDLIFE,
        ][best_index]

    is_document, _ = classifier.binary_classify_image(
        image_embedding,
        "This is a document, such as a receipt, book, "
        "ID card, passport, payment method, screenshot, event ticket, menu, "
        "recipe, or notes.",
        "This is not a document."
    )
    if is_document:
        best_index, _ = classifier.classify_image(image_embedding, [
            "This is a book or a magazine.",
            "This is a receipt or proof of payment.",
            "This is a digital screenshot from a phone or a computer.",
            "This is an event ticket, with information "
            "about the event and or the ticket holder.",
            "This is an identity document, such as an ID card, passport, "
            "drivers license, or other identifiable card.",
            "This is a person's notes, notebook, or homework.",
            "This is a payment method, such as a credit card or debit card.",
            "This is a restaurant menu.",
            "This is a recipe to create a meal.",
        ])
        document_type = [
            DocumentType.BOOK_OR_MAGAZINE,
            DocumentType.RECEIPT,
            DocumentType.SCREENSHOT,
            DocumentType.TICKET,
            DocumentType.IDENTITY,
            DocumentType.NOTES,
            DocumentType.PAYMENT_METHOD,
            DocumentType.MENU,
            DocumentType.RECIPE,
        ][best_index]

    is_object, _ = classifier.binary_classify_image(
        image_embedding,
        "This is object-focused photo, such as food, a vehicle, artwork,"
        " a device, a piece of clothing, a drink, sports equipment, or a toy.",
        "The focus is not an object."
    )
    if is_object:
        best_index, _ = classifier.classify_image(image_embedding, [
            "food",
            "car",
            "boat",
            "plane",
            "painting",
            "sculpture",
            "a device, such as a remote, or speakers, or a monitor, or a computer,"
            " or any other technological device.",
            "clothing",
            "A glass, jug, bottle or cup to drink from",
            "sports equipment",
            "document",
            "toy",
        ])
        object_type = [
            ObjectType.FOOD,
            ObjectType.CAR,
            ObjectType.BOAT,
            ObjectType.PLANE,
            ObjectType.PAINTING,
            ObjectType.SCULPTURE,
            ObjectType.DEVICE,
            ObjectType.CLOTHING,
            ObjectType.DRINK,
            ObjectType.SPORTS,
            ObjectType.DOCUMENT,
            ObjectType.TOY,
        ][best_index]

    is_activity, _ = classifier.binary_classify_image(
        image_embedding,
        "An activity is performed in this image, such as "
        "sports, fitness, dancing, photography, writing, "
        "leisure activities, traveling, camping or water activities.",
        "No activity is actively performed in this image."
    )
    if is_activity:
        best_index, _ = classifier.classify_image(
            image_embedding,
            [e.value.replace("_", " ") for e in ActivityType]
        )
        activity_type = list(ActivityType)[best_index]

    # is_event, _ = classifier.binary_classify_image(
    #     image_embedding,
    #     "An event is taking place in this image, such as "
    #     "a wedding, birthday, other celebration, party, concert, work conference, "
    #     "meeting, funeral, christmas, halloween, new years, a sports game, "
    #     "competition, marathon, protest, parade, carnival, trip or picnic.",
    #     "No specific event or celebration is happening."
    # )
    # if is_event:
    #     best_index, _ = classifier.classify_image(
    #         image_embedding,
    #         [e.value.replace("_", " ") for e in EventType]
    #     )
    #     event_type = list(EventType)[best_index]

    event_type = classifier.classify_to_enum(
        image_embedding,
        "An event is taking place in this image, such as "
        "a wedding, birthday, other celebration, party, concert, work conference, "
        "meeting, funeral, christmas, halloween, new years, a sports game, "
        "competition, marathon, protest, parade, carnival, trip or picnic.",
        "No specific event or celebration is happening.",
        EventType
    )

    is_outside, _ = classifier.binary_classify_image(
        image_embedding,
        "This is outside.",
        "This is inside."
    )
    is_landscape, _ = classifier.binary_classify_image(
        image_embedding,
        "This is a landscape featuring natural scenery such as mountains,"
        " dunes, forests, or lakes.",
        "This is not a landscape or does not feature natural scenery."
    )
    is_cityscape, _ = classifier.binary_classify_image(
        image_embedding,
        "This is a cityscape showing urban buildings, streets, or skylines.",
        "This is not a cityscape or does not feature urban areas."
    )
    is_travel, _ = classifier.binary_classify_image(
        image_embedding,
        "This photo was taken during travel, featuring landmarks, "
        "airports, or exotic locations..",
        "This photo was not taken during travel or does not suggest "
        "a travel context."
    )

    return (
        people_type,
        animal_type,
        document_type,
        object_type,
        activity_type,
        event_type,
        is_outside,
        is_landscape,
        is_cityscape,
        is_travel
    )


def experiment():
    embedder = CLIPEmbedder()
    with PIL.Image.open("../../../../media/images/1/20180815_183921.jpg") as img:
        image_embedding = embedder.embed_image(img)

        scene, conf = classify_image_scene(image_embedding)
        print(scene, conf)

        binary_dict = binary_classifications(image_embedding)
        print(binary_dict)


def frame_caption(
    visual_info: TextSummaryVisualInformation,
    pil_image: Image
) -> CaptionVisualInformation:

    return CaptionVisualInformation(
        **visual_info.model_dump(),
    )


if __name__ == "__main__":
    experiment()
