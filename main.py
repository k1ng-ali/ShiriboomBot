from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChosenInlineResult, InlineQueryResultArticle, \
    InputTextMessageContent, CallbackQuery, Message, LinkPreviewOptions
import asyncio
from game import Game, GameManager
from Utils import only_admin, AD, DailyStats, schedule_daily_stats

bot = Bot("YOUR_TOOKEN")
dp = Dispatcher()
ad = AD()

daily_stats = DailyStats()

games = GameManager()

def create_kbs(user_id: str):
    item = ["✊", "✌", "✋"]
    kbs = [InlineKeyboardButton(text=i, callback_data=f"accept:{user_id}:{i}") for i in item]
    return InlineKeyboardMarkup(inline_keyboard=[kbs])



@dp.callback_query(F.data.startswith("accept:"))
async def callback_handle(callback: CallbackQuery):
    _, inviter_id, opponent_choice = callback.data.split(":", maxsplit=2)
    opponent_id = str(callback.from_user.id)
    opponent_name = callback.from_user.full_name

    if inviter_id == opponent_id:
        return await callback.answer("Хей друг, ты не сможешь играть сам собой!", show_alert=True)

    result = games.check_result(inviter_id=inviter_id,
                                opponent_id=opponent_id,
                                opponent_choice=opponent_choice,
                                opponent_name=opponent_name)
    if result:
        games.del_game(inviter_id=inviter_id)
        text = ""
        if result.winner == "draw":
            text += "<b>Никто не выиграл!</b>\n\n"
        elif result.winner == "inviter":
            text += f"<b> {result.inviter_name} - Выиграл(а)! </b>\n\n"
        elif result.winner == "opponent":
            text += f"<b> {result.opponent_name} - Выиграл(а)! </b>\n\n"
        text += (f"<b>{result.inviter_name}</b> - выбрал(а) {result.inviter_choice}\n"
                 f"<b>{result.opponent_name}</b> - выбрал(а) {result.opponent_choice}\n\n")
        text += f"<blockquote>{ad.get_ad()}</blockquote>"
        daily_stats.inc_game()
        return await bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                           text=text,
                                           reply_markup=None,
                                           parse_mode="HTML",
                                           link_preview_options=LinkPreviewOptions(
                                               url=ad.get_link()
                                               if ad.get_link() or ad.get_link() != " "
                                               else None,
                                               prefer_small_media=True
                                           ))
    else:
        return await callback.answer("Игра уже завершена или не найдена", show_alert=True)



@dp.callback_query(F.data.startswith("stop_game:"))
async def delete_game(callback: CallbackQuery):
    _, inviter_id = callback.data.split(":", maxsplit=1)
    if inviter_id != str(callback.from_user.id):
        return await callback.answer("Вы не можете остановить чужую игру!", show_alert=True)
    game = games.get_game(inviter_id=inviter_id)
    if game and game.message_id:
        await bot.edit_message_text(
            inline_message_id=game.message_id,
            text = "Эта игра остановлена!",
            reply_markup=None
        )
        games.del_game(inviter_id=inviter_id)
        return await bot.edit_message_text(
            inline_message_id=callback.inline_message_id,
            text="Все ваши активные игры остановлены!\nПопробуйте играть снова",
            reply_markup=None
        )
    else:
        games.del_game(inviter_id=inviter_id)
        return await bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                           text="У вас нет активная ига, попробуйте играть снова. Если ошибка повторится обращайтесь: @King_a1i",
                                           reply_markup=None)


@dp.chosen_inline_result()
async def invite_game(chosen_result: ChosenInlineResult):
    _, _, inviter_choice = chosen_result.result_id.split(":", maxsplit=2)
    inviter_id = str(chosen_result.from_user.id)
    inviter_name = str(chosen_result.from_user.first_name)

    success = games.create_game(inviter_id=inviter_id,
                                 inviter_name=inviter_name,
                                 inviter_choice=inviter_choice,
                                message_id=chosen_result.inline_message_id)

    if not success:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Остановить активную игру",
                                                   callback_data=f"stop_game:{inviter_id}")]]
        )

        return await bot.edit_message_text(
            inline_message_id=chosen_result.inline_message_id,
            text = "У вас есть активная игра\n\nВы можете остановить её нажимая кнопку ниже",
            reply_markup = kb
        )


@dp.inline_query()
async def inline_query(query: types.InlineQuery):
    user_id = str(query.from_user.id)
    user_name = query.from_user.full_name

    res = []
    item = ["✊", "✌", "✋"]
    for i in item:
        res.append(
            InlineQueryResultArticle(
                id=f"inviter:{user_id}:{i}",
                title=i,
                input_message_content=InputTextMessageContent(
                    message_text=f"{user_name} приглашает вас в игру Ширибом.\nВыберите свою позицию"
                ),
                reply_markup=create_kbs(user_id)
            )
        )
    await query.answer(results=res, cache_time=0)

@only_admin
@dp.message(Command("set_ad"))
async def set_ad(msg: Message):
    ad.set_ad(msg.text.removeprefix("/set_ad").strip())
    return await msg.reply("✅ Реклама успешно установлена!")

@only_admin
@dp.message(Command("del_ad"))
async def del_ad(msg: Message):
    ad.set_ad("")
    return await msg.reply("✅ Реклама успешно удалено!")

@only_admin
@dp.message(Command("get_stats"))
async def del_ad(msg: Message):
    return await msg.reply(daily_stats.get_stats(), parse_mode="HTML")

async def main():
    asyncio.create_task(schedule_daily_stats(
        bot,stats=daily_stats
    ))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



