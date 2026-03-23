"""Message handlers — route all messages to the agent engine."""

from __future__ import annotations

import io
import logging
import os
from typing import TYPE_CHECKING

import discord
import httpx

from .formatters import extract_file_paths, format_response, make_file_attachment

if TYPE_CHECKING:
    from .bot import ArcAgentBot

logger = logging.getLogger(__name__)

TEMP_DIR = "/tmp/discord_attachments"


async def download_attachment(attachment: discord.Attachment) -> str | None:
    """Download a Discord attachment to a temp file. Returns the file path."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    filepath = os.path.join(TEMP_DIR, f"{attachment.id}_{attachment.filename}")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(attachment.url)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
        return filepath
    except Exception as e:
        logger.warning("Failed to download attachment %s: %s", attachment.filename, e)
        return None


def is_image(filename: str) -> bool:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp")


async def handle_any_message(bot: ArcAgentBot, message: discord.Message) -> None:
    """Handle any message — respond to everything."""
    content = message.content.strip()

    # Strip bot mention if present
    if bot.user:
        content = content.replace(f"<@{bot.user.id}>", "").strip()

    # Handle attachments — download them and add context to the message
    attachment_paths = []
    if message.attachments:
        for att in message.attachments:
            filepath = await download_attachment(att)
            if filepath:
                attachment_paths.append((filepath, att.filename))

        # Add attachment info to the prompt
        if attachment_paths:
            att_lines = []
            for path, name in attachment_paths:
                if is_image(name):
                    att_lines.append(
                        f"[Image attached: saved to {path}. "
                        f"Use OCR to read it: python3 -c \"from PIL import Image; import pytesseract; print(pytesseract.image_to_string(Image.open('{path}')))\"]"
                    )
                else:
                    att_lines.append(f"[File attached: saved to {path}. Read it with: cat {path}]")
            content = content + "\n\n" + "\n".join(att_lines) if content else "\n".join(att_lines)

    if not content:
        return

    # Use channel ID as conversation ID for continuity per channel
    conversation_id = str(message.channel.id)

    async with message.channel.typing():
        try:
            response = await bot.engine.send_message(conversation_id, content)

            # Save conversation to disk
            try:
                from ..core.memory import save_conversation
                conv = bot.engine.conversations.get(conversation_id)
                if conv:
                    save_conversation(conversation_id, [
                        {"role": m.role.value, "content": m.content, "timestamp": m.timestamp.isoformat()}
                        for m in conv.messages
                    ])
            except Exception as e:
                logger.warning("Failed to save conversation: %s", e)

            # Check for file paths in the response to attach
            attachments = []
            for filepath in extract_file_paths(response.text):
                attachment = make_file_attachment(filepath)
                if attachment:
                    attachments.append(attachment)

            # If response is very long, send as a file attachment
            if len(response.text) > 4000:
                text_file = discord.File(
                    io.BytesIO(response.text.encode()),
                    filename="response.md",
                )
                all_files = [text_file] + attachments
                await message.reply("Response was too long — here it is as a file:", files=all_files[:10])
            else:
                chunks = format_response(response)
                if attachments:
                    await message.reply(chunks[0], files=attachments[:10])
                else:
                    await message.reply(chunks[0])
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)

        except Exception as e:
            logger.error("Error handling message: %s", e)
            await message.reply(f"Error: {e}")
