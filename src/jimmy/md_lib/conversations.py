"""Helper functions for conversations, like facebook, signal or telegram chats."""

import dataclasses


@dataclasses.dataclass
class Message:
    r"""
    Represents a message in a conversation.

    >>> Message("aaa", "bbb").to_md()
    '**aaa**: bbb'
    >>> Message("aaa", "bbb\nccc").to_md()
    '**aaa**:\n\nbbb\nccc'
    >>> Message("", "").to_md()
    ''
    >>> Message("aaa", "bbb", quote="qqq").to_md()
    '**aaa**:\n\n> qqq\n\nbbb'
    >>> Message("aaa", "bbb", quote="qqq\nppp").to_md()
    '**aaa**:\n\n> qqq\n> ppp\n\nbbb'
    >>> Message("aaa", "bbb", attachment_links=["link"]).to_md()
    '**aaa**: bbb\n\nlink'
    >>> Message("aaa", "", attachment_links=["link"]).to_md()
    '**aaa**: link'
    >>> Message("aaa", "", attachment_links=["link1", "link2"]).to_md()
    '**aaa**:\n\nlink1\n\nlink2'
    """

    author: str
    text: str
    prefix: str = ""
    attachment_links: list[str] = dataclasses.field(default_factory=list)
    # quote of some previous message
    quote: str = ""

    def to_md(self) -> str:
        text = self.text.strip()
        if not text and not self.attachment_links and not self.quote:
            return ""
        md_message = f"{self.prefix}, " if self.prefix else ""
        md_message += f"**{self.author}**:"
        if self.quote:
            md_message += (
                "\n\n"
                + ("\n".join("> " + quote_line for quote_line in self.quote.strip().split("\n")))
                + "\n\n"
            )

        if text:
            # single line messages start on the same line
            # multiline messages start on the next line
            if "\n" in text:
                md_message += "\n\n"
            elif not self.quote:
                md_message += " "
            md_message += text

        if not self.text and not self.quote and len(self.attachment_links) == 1:
            # single attachment on the same line
            md_message += " " + self.attachment_links[0]
        else:
            for attachment_link in self.attachment_links:
                md_message += "\n\n" + attachment_link

        return md_message


@dataclasses.dataclass
class Conversation:
    """Represents a conversation."""

    messages: list[Message] = dataclasses.field(default_factory=list)

    def to_md(self):
        md_list = []
        for message in self.messages:
            if md_message := message.to_md():
                md_list.append(md_message)

        if md_list:
            return "\n\n".join(md_list) + "\n"
        return ""
