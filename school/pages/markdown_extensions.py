from xml.etree.ElementTree import ElementTree

from django.conf import settings
from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor


class SchoolImageTreeprocessor(Treeprocessor):
    def run(self, root: ElementTree):
        for elem in root.iter("img"):
            image_url = elem.get("src")
            print("imageeeee")
            if image_url is None:
                continue

            # External images
            if image_url.startswith("http://") or image_url.startswith("https://"):
                continue

            # Already MEDIA images
            if image_url.startswith(settings.MEDIA_URL):
                continue

            elem.set(
                "src",
                "/".join(
                    map(
                        lambda x: x.strip("/"),
                        ["", settings.MEDIA_URL, "assets", image_url],
                    )
                ),
            )


class SchoolImageExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.treeprocessors.register(SchoolImageTreeprocessor(md), "ksp_school_images", 0)
