import re
from xml.etree.ElementTree import Element, SubElement

from django.conf import settings
from markdown import Extension, Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


class SchoolImageTreeprocessor(Treeprocessor):
    def run(self, root: Element):
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
    def run(self, lines: list[str]) -> list[str]:
        new_lines = []
        inside = 0
        for line in lines:
            # when editing content via admin, some browsers use \r\n line ending
            if line.endswith("\r"):
                line = line[:-1]

            if line == "```vstup":
                new_lines.append("<io>")
                new_lines.append("<io:input>")
                new_lines.append("```")
                inside = 1
            elif line == "```vystup":
                new_lines.append("<io:output>")
                new_lines.append("```")
                inside = 3
            elif line == "```":
                new_lines.append("```")
                if inside == 3:
                    new_lines.append("</io:output>\n")
                    new_lines.append("</io>")
                    inside = 0
                elif inside == 1:
                    new_lines.append("</io:input>\n")
                    inside = 2
            else:
                new_lines.append(line)
        return new_lines


class FencedBlockProcessor(BlockProcessor):
    RE_FENCE_START: str
    RE_FENCE_END: str

    def test(self, parent: Element, block: str) -> bool:
        return re.match(self.RE_FENCE_START, block) is not None

    def fence_logic(self, parent: Element, blocks: list[str]) -> None:
        raise NotImplementedError()

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, "", blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, "", block)

                self.fence_logic(parent, blocks[0 : block_num + 1])

                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class BoxBlockProcessor(FencedBlockProcessor):
    RE_FENCE_START = r"<io>"
    RE_FENCE_END = r"</io>"

    def fence_logic(self, parent, blocks):
        d = SubElement(parent, "div")
        d.set("class", "io")
        self.parser.parseBlocks(d, blocks)


class IOInputBlockProcessor(FencedBlockProcessor):
    RE_FENCE_START = r"<io:input>"
    RE_FENCE_END = r"</io:input>"

    def fence_logic(self, parent, blocks):
        d = SubElement(parent, "div")
        inp = SubElement(d, "h3")
        inp.text = "Vstup"
        self.parser.parseBlocks(d, blocks)


class IOOutputBlockProcessor(FencedBlockProcessor):
    RE_FENCE_START = r"<io:output>"
    RE_FENCE_END = r"</io:output>"

    def fence_logic(self, parent, blocks):
        d = SubElement(parent, "div")
        inp = SubElement(d, "h3")
        inp.text = "Výstup"
        self.parser.parseBlocks(d, blocks)


class KspSchoolExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        md.treeprocessors.register(SchoolImageTreeprocessor(md), "ksp_school_images", 0)
        md.preprocessors.register(CodeBlocksProcessor(md), "IO_code_blocks", 100000)
        md.parser.blockprocessors.register(
            BoxBlockProcessor(md.parser), "IO_box", 100000
        )
        md.parser.blockprocessors.register(
            IOInputBlockProcessor(md.parser), "IO_input", 100000
        )
        md.parser.blockprocessors.register(
            IOOutputBlockProcessor(md.parser), "IO_output", 100000
        )
