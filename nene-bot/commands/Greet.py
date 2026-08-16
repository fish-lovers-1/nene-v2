from typing import Literal

from discord.ext import commands

SupportedLanguage = Literal["EN", "JP"]

_GREETING = {
    "EN": "Kon Nene! The Ne of NePoLaBo. The energy drink for everyone's heart. It's me, Momosuzu Nene!",
    "JP": "こんねね！ホロライブ５期生めぽらぼのね。みんなの心のエネルギードリンク。桃鈴ねねです！",
}


class Greet(commands.Cog):
    def __init__(self, nene: commands.Bot):
        super().__init__()
        self.nene = nene

    @commands.command()
    async def greet(
        self,
        ctx: commands.Context,
        language: SupportedLanguage = commands.parameter(
            description="Language Nene will greet you in. only available in JP or EN",
            default="EN",
        ),
    ):
        await ctx.reply(_GREETING[language])
