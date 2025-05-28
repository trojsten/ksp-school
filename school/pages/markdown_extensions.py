import re
from xml.etree.ElementTree import ElementTree, SubElement

from django.conf import settings
from markdown import Extension, Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


class SchoolImageTreeprocessor(Treeprocessor):
    def run(self, root: ElementTree):
        for elem in root.iter("img"):
            image_url = elem.get("src")
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


class CodeBlocksProcessor(Preprocessor):
    def run(self, lines) -> list[str]:
        new_lines = []
        inside = 0
        for line in lines:
            # when editing content via admin, some browsers use \r\n line ending
            if line.endswith("\r"):
                line = line[:-1]

            if line == "```vstup":
                new_lines.append("<io>")
                # new_lines.append("### Vstup")
                new_lines.append("```")
                inside = 1
            elif line == "```vystup":
                # new_lines.append("### Výstup")
                new_lines.append("```")
                inside = 2
            elif line == "```" and inside == 2:
                new_lines.append("```")
                new_lines.append("</io>")
                inside = 0
            else:
                new_lines.append(line)
        return new_lines


class BoxBlockProcessor(BlockProcessor):
    RE_FENCE_START = r"<io>"
    RE_FENCE_END = r"</io>"

    def test(self, parent, block) -> bool:
        return re.match(self.RE_FENCE_START, block) is not None

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, "", blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, "", block)
                # render fenced area inside a new div
                e = SubElement(parent, "div")
                e.set("class", "io")
                inp = SubElement(e, "h3")
                inp.text = "Vstup"
                out = SubElement(e, "h3")
                out.text = "Výstup"

                self.parser.parseBlocks(e, blocks[0 : block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class KspSchoolExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        md.treeprocessors.register(SchoolImageTreeprocessor(md), "ksp_school_images", 0)
        md.preprocessors.register(CodeBlocksProcessor(md), "IO_code_blocks", 100000)
        md.parser.blockprocessors.register(BoxBlockProcessor(md.parser), "box", 100000)
