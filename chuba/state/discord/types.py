
from typing import Any, Dict, List
from discord import File, User, Embed, Member, Message
from discord_components import Button, Select, SelectOption

from .event import DiscordStateEventType
from chuba.state.types import event, State, StateEvent, StateContext
from chuba.state.discord import (
    DiscordStateEventType,
    ButtonEvent,
    MessageEvent,
    SelectEvent)


def button(**filers):
    return event(DiscordStateEventType.BUTTON, **filers)


def message(**filters):
    return event(DiscordStateEventType.MESSAGE, **filters)


def select(**filters):
    return event(DiscordStateEventType.SELECT, **filters)


class DiscordMessageStateForm:
    """Форма, описывающая дискорд сообщение

    Данной форме можно задать сообщение, эмбед, файлы, картинки и view-компоненты (Кнопки)
    """

    data: dict

    def build_selector_layout(self, raw_select) -> Select:
        return Select.from_json(raw_select)

    def build_button_layout(self, raw_button_layout) -> List[Button | List[Button]]:
        layout = []
        for value in raw_button_layout:
            if isinstance(value, dict):
                layout.append(Button.from_json(value))
            elif isinstance(value, list):
                layout.append(self.build_button_layout(value))
        return layout

    @property
    def files_raw(self) -> List[str]:
        return self.data.get("files", [])

    @property
    def button_layout_raw(self) -> List:
        return self.data.get("buttons", None)

    @property
    def embed_raw(self) -> Dict[str, Any]:
        return self.data.get("embed", {})

    @property
    def select_raw(self) -> Dict[str, Any]:
        return self.data.get("select", None)

    @property
    def file(self) -> File:
        file_path = self.data.get("file")
        return File(file_path) if file_path else None

    @property
    def files(self) -> List[File]:
        return [File(f) for f in self.files_raw]

    @property
    def embed(self) -> Embed:
        return Embed.from_dict(self.embed_raw)

    @property
    def content(self) -> str | None:
        return self.data.get("content", None)

    @property
    def component_layout(self) -> List:
        components = []
        if self.select_raw:
            components.append(self.build_selector_layout(self.select_raw))
        if self.button_layout_raw:
            components.extend(self.build_button_layout(self.button_layout_raw))
        return components

    def to_send(self):
        return {
            "embed": self.embed,
            "file": self.file,
            "files": self.files,
            "content": self.content,
            "components": self.component_layout
        }


class DiscordMessageState(State):
    """Дискорд состояние

    Обычное состояние, разве что позволяет отослать пользователю сообщение/эмбед/файлы и прочее, сразу как только
    состояние будет задано.
    """

    form: DiscordMessageStateForm = None
    """Форма, которая будет отправлена пользователю, когда для него будет задано данное состояние
    """

    async def show(self, ctx: StateContext, **kwargs) -> Message:
        user = ctx.user
        event = ctx.event
        if isinstance(event, MessageEvent):
            return await user.send(**kwargs)
        elif isinstance(event, ButtonEvent) or isinstance(event, SelectEvent):
            if not event.interaction.responded:
                await event.interaction.edit_origin(**kwargs)
            else:
                await event.interaction.message.edit(**kwargs)
            return event.interaction.message
        else:
            return await user.send(**kwargs)

    async def setup(self, ctx: StateContext) -> None:
        await super().setup(ctx)

        await self.show(
            ctx,
            embed=self.form.embed,
            files=self.form.files,
            content=self.form.content,
            components=self.form.component_layout
        )
