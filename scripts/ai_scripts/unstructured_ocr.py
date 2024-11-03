from unstructured.partition.image import partition_image

# Returns a List[Element] present in the pages of the parsed image document
elements = partition_image("ocr.jpg")

out_txt = ""
for element in elements:
    if hasattr(element, 'text'):
        out_txt += element.text.strip() + "\n"

print(out_txt)
