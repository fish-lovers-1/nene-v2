import discord.ext.test as dpytest
import pytest

from nene.Nene import Nene


@pytest.mark.parametrize(("lang_arg"), ["EN", ""])
@pytest.mark.asyncio
async def test_greet_en(test_nene: Nene, lang_arg: str):
    await dpytest.message(f"Nene greet {lang_arg}")
    assert (
        dpytest.verify()
        .message()
        .content(
            "Kon Nene! The Ne of NePoLaBo. The energy drink for everyone's heart. It's me, Momosuzu Nene!"
        )
    )


@pytest.mark.asyncio
async def test_greet_jp(test_nene: Nene):
    await dpytest.message("Nene greet JP")
    assert (
        dpytest.verify()
        .message()
        .content(
            "こんねね！ホロライブ５期生めぽらぼのね。みんなの心のエネルギードリンク。桃鈴ねねです！"
        )
    )
