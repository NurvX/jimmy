"""Convert Telegram chats to the intermediate format."""

import json
from pathlib import Path

from jimmy import common, converter, intermediate_format as imf
import jimmy.md_lib.conversations
import jimmy.md_lib.links


class Converter(converter.BaseConverter):
    @common.catch_all_exceptions()
    def convert_note(self, chat):
        if chat.get("type", "") == "saved_messages":
            title = "Saved Messages"
        else:
            title = chat.get("name", "Unnamed Chat")
        self.logger.debug(f'Converting chat "{title}"')
        note_imf = imf.Note(title, source_application=self.format, original_id=str(chat["id"]))

        md_conversation = jimmy.md_lib.conversations.Conversation()
        for message in chat["messages"]:
            if message["type"] != "service" and message.get("action") == "create_group":
                note_imf.created = common.timestamp_to_datetime(int(message["date_unixtime"]))
            if message["type"] != "message":
                continue

            message_time = common.timestamp_to_datetime(int(message["date_unixtime"]))
            md_message = jimmy.md_lib.conversations.Message(
                message["from"],
                message.get("text", ""),
                prefix=message_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            if (file_ := message.get("file")) is not None:
                file_md = jimmy.md_lib.links.make_link(
                    message.get("file_name", ""), str(self.root_path / file_), is_image=True
                )
                note_imf.resources.append(
                    imf.Resource(self.root_path / file_, file_md, message.get("file_name"))
                )
                md_message.attachment_links.append(file_md)

            md_conversation.messages.append(md_message)

            # update the updated time each message to get the timestamp
            # of the last message at the end
            note_imf.updated = message_time
        note_imf.body = md_conversation.to_md()

        if not note_imf.body:
            self.logger.debug("Skipping empty chat.")
            return

        self.root_notebook.child_notes.append(note_imf)

    def convert(self, file_or_folder: Path):
        input_json = json.loads((file_or_folder / "result.json").read_text(encoding="utf-8"))
        if (chats := input_json.get("chats")) is not None:
            self.logger.debug('Found "chats" key. Assuming that this is a complete "DataExport".')
            for chat in chats["list"]:
                self.convert_note(chat)
        else:
            self.logger.debug('No "chats" key. Assuming that this is a single "ChatExport".')
            self.convert_note(input_json)
