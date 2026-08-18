import json
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

# --- НАСТРОЙКА ---
BOT_TOKEN = '8912498030:AAHKq4rLQQNG1m8jhu1hEbPRwim-FQXq-Fg'
DATA_FILE = 'cashflow_data.json'

# --- БАЗА ДАННЫХ 11 ПРОФЕССИЙ ---
PROFESSIONS = {
    "Учитель": {"name": "Учитель", "salary": 3300, "assets": {"savings": 400},
                "liabilities": {"mortgage": 50000, "student_loan": 12000, "car_loan": 5000, "credit_cards": 3000,
                                "purchase_debt": 1000},
                "expenses": {"taxes": 630, "mortgage": 500, "student_loan": 60, "car_loan": 100, "credit_cards": 90,
                             "purchase_debt": 50, "other": 760, "children_initial": 0, "child_cost": 180}},
    "Бизнес_менеджер": {"name": "Бизнес менеджер", "salary": 4600, "assets": {"savings": 400},
                        "liabilities": {"mortgage": 75000, "student_loan": 12000, "car_loan": 6000,
                                        "credit_cards": 3000, "purchase_debt": 1000},
                        "expenses": {"taxes": 910, "mortgage": 700, "student_loan": 60, "car_loan": 120,
                                     "credit_cards": 90, "purchase_debt": 50, "other": 1000, "children_initial": 0,
                                     "child_cost": 240}},
    "Доктор": {"name": "Доктор", "salary": 13200, "assets": {"savings": 400},
               "liabilities": {"mortgage": 202000, "student_loan": 150000, "car_loan": 19000, "credit_cards": 9000,
                               "purchase_debt": 1000},
               "expenses": {"taxes": 3420, "mortgage": 1900, "student_loan": 750, "car_loan": 380, "credit_cards": 270,
                            "purchase_debt": 50, "other": 2880, "children_initial": 0, "child_cost": 640}},
    "Адвокат": {"name": "Адвокат", "salary": 7500, "assets": {"savings": 400},
                "liabilities": {"mortgage": 115000, "student_loan": 78000, "car_loan": 11000, "credit_cards": 6000,
                                "purchase_debt": 1000},
                "expenses": {"taxes": 1830, "mortgage": 1100, "student_loan": 390, "car_loan": 220, "credit_cards": 180,
                             "purchase_debt": 50, "other": 1650, "children_initial": 0, "child_cost": 380}},
    "Медсестра": {"name": "Медсестра", "salary": 3100, "assets": {"savings": 520},
                  "liabilities": {"mortgage": 47000, "student_loan": 6000, "car_loan": 5000, "credit_cards": 3000,
                                  "purchase_debt": 1000},
                  "expenses": {"taxes": 600, "mortgage": 400, "student_loan": 30, "car_loan": 100, "credit_cards": 90,
                               "purchase_debt": 50, "other": 710, "children_initial": 0, "child_cost": 170}},
    "Инженер": {"name": "Инженер", "salary": 4900, "assets": {"savings": 400},
                "liabilities": {"mortgage": 75000, "student_loan": 12000, "car_loan": 7000, "credit_cards": 4000,
                                "purchase_debt": 1000},
                "expenses": {"taxes": 1050, "mortgage": 700, "student_loan": 60, "car_loan": 140, "credit_cards": 120,
                             "purchase_debt": 50, "other": 1090, "children_initial": 0, "child_cost": 250}},
    "Секретарь": {"name": "Секретарь", "salary": 2500, "assets": {"savings": 520},
                  "liabilities": {"mortgage": 38000, "student_loan": 0, "car_loan": 4000, "credit_cards": 2000,
                                  "purchase_debt": 1000},
                  "expenses": {"taxes": 460, "mortgage": 400, "student_loan": 0, "car_loan": 80, "credit_cards": 60,
                               "purchase_debt": 50, "other": 570, "children_initial": 0, "child_cost": 140}},
    "Водитель_грузовика": {"name": "Водитель грузовика", "salary": 2500, "assets": {"savings": 750},
                           "liabilities": {"mortgage": 38000, "student_loan": 0, "car_loan": 4000, "credit_cards": 2000,
                                           "purchase_debt": 1000},
                           "expenses": {"taxes": 460, "mortgage": 400, "student_loan": 0, "car_loan": 80,
                                        "credit_cards": 60, "purchase_debt": 50, "other": 570, "children_initial": 0,
                                        "child_cost": 140}},
    "Уборщица": {"name": "Уборщица", "salary": 1600, "assets": {"savings": 560},
                 "liabilities": {"mortgage": 20000, "student_loan": 0, "car_loan": 4000, "credit_cards": 2000,
                                 "purchase_debt": 1000},
                 "expenses": {"taxes": 280, "mortgage": 200, "student_loan": 0, "car_loan": 60, "credit_cards": 60,
                              "purchase_debt": 50, "other": 300, "children_initial": 0, "child_cost": 70}},
    "Авиапилот": {"name": "Авиапилот", "salary": 9500, "assets": {"savings": 400},
                  "liabilities": {"mortgage": 143000, "student_loan": 0, "car_loan": 15000, "credit_cards": 22000,
                                  "purchase_debt": 1000},
                  "expenses": {"taxes": 2350, "mortgage": 1330, "student_loan": 0, "car_loan": 300, "credit_cards": 660,
                               "purchase_debt": 50, "other": 2210, "children_initial": 0, "child_cost": 480}},
    "Механик": {"name": "Механик", "salary": 2000, "assets": {"savings": 670},
                "liabilities": {"mortgage": 31000, "student_loan": 0, "car_loan": 3000, "credit_cards": 2000,
                                "purchase_debt": 1000},
                "expenses": {"taxes": 360, "mortgage": 300, "student_loan": 0, "car_loan": 60, "credit_cards": 60,
                             "purchase_debt": 50, "other": 450, "children_initial": 0, "child_cost": 110}}
}


# --- ЛОГИКА РАБОТЫ С ДАННЫМИ ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_player(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "profession": None, "game_phase": "inner", "cash": 0, "salary": 0,
            "expenses": {}, "assets": {"savings": 0, "investments": []},
            "liabilities": {}, "children": 0, "bank_loan": 0,
            "outer_assets": [], "outer_financial_goal": 0
        }
        save_data(data)
    else:
        # Автоматическое восстановление полей, если вы обновляете код
        if 'profession' not in data[user_id]: data[user_id]['profession'] = None
        if 'game_phase' not in data[user_id]: data[user_id]['game_phase'] = "inner"
        if 'outer_assets' not in data[user_id]: data[user_id]['outer_assets'] = []
        if 'bank_loan' not in data[user_id]: data[user_id]['bank_loan'] = 0
    return data[user_id]


def update_player(user_id, updated_data):
    data = load_data()
    data[str(user_id)] = updated_data
    save_data(data)


# --- РАСЧЕТ ФИНАНСОВ (С УЧЕТОМ 10% КРЕДИТА) ---
def calculate_finances(p):
    total_income = p['salary']
    passive_income = 0
    for inv in p['assets']['investments']:
        total_income += inv['income'] * inv['qty']
        passive_income += inv['income'] * inv['qty']

    total_expenses = sum(p['expenses'].values())
    child_cost = p['expenses'].get('child_cost', 0) * p['children']
    total_expenses += child_cost

    # Расчет 10% от долга банку
    bank_interest = int(p['bank_loan'] * 0.1)
    total_expenses += bank_interest

    cash_flow = total_income - total_expenses
    return total_income, total_expenses, cash_flow, passive_income, bank_interest


# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# --- МАШИНА СОСТОЯНИЙ (ДЛЯ ВСЕХ ДИАЛОГОВ) ---
class CashflowStates(StatesGroup):
    w_asset_name = State()
    w_asset_type = State()
    w_asset_price = State()
    w_asset_income = State()
    w_asset_qty = State()

    w_realize_name = State()
    w_realize_qty = State()

    w_outer_name = State()
    w_outer_cost = State()
    w_outer_income = State()
    w_outer_expense = State()

    w_add_cash = State()
    w_sub_cash = State()

    w_event_fire = State()
    w_event_charity = State()
    w_event_junk = State()

    # Новое состояние для кредита
    w_take_loan_amount = State()


# --- КЛАВИАТУРЫ ---
def get_inner_keyboard():
    kb = [
        [types.InlineKeyboardButton(text="📊 Мой профиль", callback_data="profile")],
        [types.InlineKeyboardButton(text="📦 Мои активы", callback_data="view_assets")],
        [types.InlineKeyboardButton(text="💰 Следующий круг", callback_data="next_round")],
        [types.InlineKeyboardButton(text="👶 Прибавление", callback_data="add_child")],
        [types.InlineKeyboardButton(text="🏦 Взять кредит", callback_data="take_loan")],
        [types.InlineKeyboardButton(text="⚡ Действие на поле", callback_data="field_action")],
        [types.InlineKeyboardButton(text="💵 Пополнить/Снять", callback_data="adjust_cash")],
        [types.InlineKeyboardButton(text="🔄 Сменить профессию", callback_data="choose_profession")]
        [types.InlineKeyboardButton(text="🗑️ Завершить игру (Сброс)", callback_data="reset_game")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_outer_keyboard():
    kb = [
        [types.InlineKeyboardButton(text="📊 Мой профиль", callback_data="profile")],
        [types.InlineKeyboardButton(text="📦 Мои активы", callback_data="view_assets")],
        [types.InlineKeyboardButton(text="💰 Реализовать бизнес", callback_data="realize_business")],
        [types.InlineKeyboardButton(text="💼 Купить бизнес (Внешний)", callback_data="buy_outer_asset")],
        [types.InlineKeyboardButton(text="🏁 Выход из игры", callback_data="exit_game")]
        [types.InlineKeyboardButton(text="🗑️ Завершить игру (Сброс)", callback_data="reset_game")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_profession_keyboard():
    kb = []
    for p_name in PROFESSIONS.keys():
        kb.append([types.InlineKeyboardButton(text=p_name, callback_data=f"prof_{p_name}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# --- ОБРАБОТЧИКИ КОМАНД ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    p = get_player(user_id)
    
    # 1. ВСЕГДА ПОКАЗЫВАЕМ ИНСТРУКЦИЮ ПЕРВЫМ СООБЩЕНИЕМ
    await message.answer(
        f"🎲 **Добро пожаловать в помощник игры Cashflow (Крысиные бега)!**\n\n"
        f"Этот бот заменит вам бумажные бланки и калькулятор.\n"
        f"Все расчеты происходят автоматически.\n\n"
        f"📌 **Как начать игру:**\n"
        f"1. Получите случайную карточку профессии из колоды.\n"
        f"2. Выберите её в боте.\n"
        f"3. Бот загрузит ваш стартовый бюджет.\n\n"
        f"---\n\n"
        f"🕹️ **Управление ботом:**\n\n"
        f"📊 **Мой профиль:** Показывает ваш баланс, денежный поток, расходы, долги и условия выхода на Внешний Круг.\n\n"
        f"📦 **Мои активы:** Просмотр купленных активов. Здесь же можно **купить новый актив** или **продать** имеющийся.\n\n"
        f"💰 **Следующий круг:** Начисляет ежемесячный денежный поток на счет (зарплата).\n\n"
        f"👶 **Прибавление:** Если выпала ячейка «Ребенок», нажмите эту кнопку. Расходы увеличатся (max 3 детей).\n\n"
        f"🏦 **Взять кредит:** Возьмите деньги в долг если нужно.\n\n"
        f"⚡ **Действие на поле:** Увольнение, благотворительность, безделушки, выплата долгов.\n\n"
        f"💵 **Пополнить/Снять:** Ручная корректировка наличных (использовать для Увольнение, Благотворительность).\n\n"
        f"🔄 **Сменить профессию:** Можно изменить карточу профессии.\n\n"
        f"🗑️ **Завершить игру (Сброс):** Завершает игру, сбрасываю прогресс.\n\n"
        f"---\n\n"
        f"🎯 **Цель игры:** Пассивный доход > Расходы, и все долги погашены.\n\n"
        f"🍀 **Удачи и финансового роста!**",
        parse_mode="Markdown"
    )

    # 2. ТЕПЕРЬ ПОКАЗЫВАЕМ КНОПКИ (в зависимости от того, есть ли профессия)
    if p['profession'] is None:
        # Если профессии нет -> кнопки выбора профессии
        await message.answer(
            f"Выберите вашу профессию, чтобы начать игру:",
            reply_markup=get_profession_keyboard()
        )
    else:
        # Если профессия уже есть -> кнопки главного меню
        ti, te, cf, pi, bi = calculate_finances(p)
        await message.answer(
            f"👋 С возвращением!\nТы играешь за **{p['profession']}**.\n💰 Баланс: **${p['cash']}**\n📊 Денежный поток: **${cf}**",
            parse_mode="Markdown",
            reply_markup=get_outer_keyboard() if p['game_phase']=="outer" else get_inner_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith("prof_"))
async def process_choose_profession(callback_query: CallbackQuery):
    prof_name = callback_query.data.replace("prof_", "")
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if prof_name in PROFESSIONS:
        d = PROFESSIONS[prof_name]
        p['profession'] = prof_name
        p['cash'] = d['assets']['savings']
        p['salary'] = d['salary']
        p['expenses'] = {k: v for k, v in d['expenses'].items() if k != 'child_cost'}
        p['assets']['savings'] = d['assets']['savings']
        p['assets']['investments'] = []
        p['liabilities'] = d['liabilities'].copy()
        p['children'] = 0
        p['game_phase'] = "inner"
        p['outer_assets'] = []
        p['bank_loan'] = 0
        update_player(user_id, p)
        await callback_query.message.edit_text(f"✅ Ты выбрал **{prof_name}**! Удачи!", parse_mode="Markdown",
                                               reply_markup=get_inner_keyboard())
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "choose_profession")
async def process_change_prof(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    p['game_phase'] = "inner"
    p['bank_loan'] = 0
    update_player(user_id, p)
    await callback_query.message.edit_text("Выбери новую профессию:", reply_markup=get_profession_keyboard())
    await callback_query.answer()


# --- ПРОФИЛЬ И КРУГ ---
@dp.callback_query(lambda c: c.data == "profile")
async def process_profile(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    ti, te, cf, pi, bi = calculate_finances(p)
    total_debts = sum(p['liabilities'].values()) + p['bank_loan']

    text = f"👤 **{p['profession']}**\n"
    if p['game_phase'] == "inner":
        text += f"📍 Стадия: Крысиные бега\n💰 Наличные: ${p['cash']}\n📊 Денежный поток: ${cf}\n"
        text += f"📈 Пассивный доход: ${pi}\n📉 Общий расход: ${te}\n👶 Детей: {p['children']}\n\n"
        text += f"🏦 Долг банку: ${p['bank_loan']} (Проценты: ${bi}/круг)\n"
        text += f"💳 Другие долги: ${total_debts - p['bank_loan']}\n"
        if pi > te and total_debts == 0:
            text += "\n🔥 **УСЛОВИЯ ВЫХОДА ВЫПОЛНЕНЫ!** Нажми «Сменить профессию»."
    else:
        text += f"📍 Стадия: Внешний круг\n💰 Наличные: ${p['cash']}\n📊 Портфель бизнесов: {len(p['outer_assets'])} шт."
    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_outer_keyboard() if p[
                                                                                                                 'game_phase'] == "outer" else get_inner_keyboard())
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "next_round")
async def process_next_round(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    ti, te, cf, pi, bi = calculate_finances(p)
    p['cash'] += cf
    update_player(user_id, p)
    await callback_query.message.edit_text(f"🔄 Заработано: +${cf}. Баланс: ${p['cash']}.",
                                           reply_markup=get_inner_keyboard())
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "add_child")
async def process_add_child(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if p['children'] >= 3:
        await callback_query.answer("Больше 3 детей нельзя!", show_alert=True)
        return
    p['children'] += 1
    update_player(user_id, p)
    await callback_query.message.edit_text(f"👶 Теперь {p['children']} ребенок(а)!", reply_markup=get_inner_keyboard())
    await callback_query.answer()


# --- ВЗЯТИЕ КРЕДИТА ---
@dp.callback_query(lambda c: c.data == "take_loan")
async def start_take_loan(callback_query: CallbackQuery, state: FSMContext):
    # Создаем клавиатуру с кнопкой Назад
    kb = [
        [types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    await callback_query.message.edit_text(
        "🏦 Введите сумму, которую хотите взять в кредит у банка:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.set_state(CashflowStates.w_take_loan_amount)
    await callback_query.answer()


@dp.message(CashflowStates.w_take_loan_amount)
async def process_take_loan_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите целое число.")
        return
    amount = int(message.text)
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше 0.")
        return

    user_id = message.from_user.id
    p = get_player(user_id)
    p['cash'] += amount
    p['bank_loan'] += amount
    update_player(user_id, p)

    await message.answer(f"🏦 Кредит оформлен! +${amount} наличных.\nЕжемесячная плата: ${int(amount * 0.1)} (10%).",
                         parse_mode="Markdown", reply_markup=get_inner_keyboard())
    await state.clear()


# --- ВЫПЛАТА ДОЛГОВ И КРЕДИТА (В МЕНЮ "ДЕЙСТВИЕ НА ПОЛЕ") ---
@dp.callback_query(lambda c: c.data == "pay_liability")
async def start_pay_liability(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if p['game_phase'] != "inner":
        await callback_query.answer("Это работает только в Крысиных бегах!", show_alert=True)
        return

    kb = []
    # Список пассивов из карточки
    for key, val in p['liabilities'].items():
        if val > 0:
            kb.append([types.InlineKeyboardButton(text=f"{key} (-${val})", callback_data=f"pay_{key}")])
    # Список кредита банка
    if p['bank_loan'] > 0:
        kb.append(
            [types.InlineKeyboardButton(text=f"Кредит банка (-${p['bank_loan']})", callback_data="pay_bank_loan")])

    if not kb:
        await callback_query.message.edit_text("У тебя нет долгов!", reply_markup=get_inner_keyboard())
        await callback_query.answer()
        return

    kb.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="profile")])
    await callback_query.message.edit_text("💸 Какой долг хочешь выплатить?",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("pay_"))
async def process_pay_liability(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data.replace("pay_", "")
    user_id = callback_query.from_user.id
    p = get_player(user_id)

    # Обработка погашения кредита банка
    if action == "bank_loan":
        await callback_query.message.edit_text(
            f"💸 У тебя долг банку ${p['bank_loan']}.\nВведи сумму, которую хочешь погасить сейчас:")
        await state.set_state(CashflowStates.w_sub_cash)
        await state.update_data(pay_type="bank_loan")
        await callback_query.answer()
        return

    # Обработка стандартных долгов из карточки
    mapping = {
        "mortgage": ("mortgage", "mortgage"),
        "student_loan": ("student_loan", "student_loan"),
        "car_loan": ("car_loan", "car_loan"),
        "credit_cards": ("credit_cards", "credit_cards"),
        "purchase_debt": ("purchase_debt", "purchase_debt")
    }
    if action in mapping:
        debt_key, expense_key = mapping[action]
        cost = p['liabilities'][debt_key]
        if p['cash'] >= cost:
            p['cash'] -= cost
            p['liabilities'][debt_key] = 0
            p['expenses'][expense_key] = 0
            update_player(user_id, p)
            await callback_query.message.edit_text(f"✅ {debt_key} выплачен! -${cost} с баланса.",
                                                   reply_markup=get_inner_keyboard())
        else:
            await callback_query.answer(f"❌ Не хватает денег! Нужно ${cost}.", show_alert=True)
    await callback_query.answer()


@dp.message(CashflowStates.w_sub_cash)
async def process_pay_bank_loan_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return

    data = await state.get_data()
    if data.get("pay_type") == "bank_loan":
        amount = int(message.text)
        user_id = message.from_user.id
        p = get_player(user_id)

        if amount <= 0:
            await message.answer("❌ Введите сумму больше 0.")
            return
        if amount > p['cash']:
            await message.answer(f"❌ Не хватает наличных! У тебя ${p['cash']}.")
            return
        if amount > p['bank_loan']:
            amount = p['bank_loan']

        p['cash'] -= amount
        p['bank_loan'] -= amount
        update_player(user_id, p)
        await message.answer(f"✅ Кредит банку погашен на ${amount}! Остаток: ${p['bank_loan']}.",
                             reply_markup=get_inner_keyboard())
        await state.clear()


# --- ОСТАЛЬНЫЕ РАЗДЕЛЫ (АКТИВЫ, ПОЛЕ, НАЛИЧНЫЕ) ---
@dp.callback_query(lambda c: c.data == "view_assets")
async def process_view_assets(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)

    # Готовим клавиатуру. Она будет показываться в любом случае!
    kb = [
        [types.InlineKeyboardButton(text="📈 Купить актив", callback_data="buy_asset")],
        [types.InlineKeyboardButton(text="🔙 В профиль", callback_data="profile")]
    ]

    if not p['assets']['investments']:
        # Если активов нет, показываем текст + кнопку купить
        await callback_query.message.edit_text(
            "📦 У тебя пока нет купленных активов.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        await callback_query.answer()
        return

    # Если активы есть, показываем их список + кнопки купить/продать
    text = "📦 **Твои активы:**\n\n"
    for i, inv in enumerate(p['assets']['investments']):
        text += f"{i + 1}. {inv['name']} ({inv['type']})\n   Кол-во: {inv['qty']} шт.\n   Цена: ${inv['price']}/шт.\n   Доход: +${inv['income']}/шт.\n   **Общий доход: +${inv['income'] * inv['qty']}**\n\n"

    # Добавляем кнопку продажи в список, если активы есть
    kb.insert(0, [types.InlineKeyboardButton(text="📉 Продать актив", callback_data="sell_asset_menu")])

    await callback_query.message.edit_text(text, parse_mode="Markdown",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "sell_asset_menu")
async def start_sell_asset(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if not p['assets']['investments']:
        await callback_query.answer("Активов для продажи нет.", show_alert=True)
        return
    kb = []
    for i, inv in enumerate(p['assets']['investments']):
        kb.append([types.InlineKeyboardButton(text=f"{inv['name']} ({inv['qty']} шт.)", callback_data=f"sell_{i}")])
    kb.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="view_assets")])
    await callback_query.message.edit_text("📉 Какой актив хочешь продать?",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "sell_asset_menu")
async def start_sell_asset(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if not p['assets']['investments']:
        await callback_query.answer("Активов для продажи нет.", show_alert=True)
        return
    kb = []
    for i, inv in enumerate(p['assets']['investments']):
        kb.append([types.InlineKeyboardButton(text=f"{inv['name']} ({inv['qty']} шт.)", callback_data=f"sell_{i}")])
    kb.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="view_assets")])
    await callback_query.message.edit_text("📉 Какой актив хочешь продать?",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("sell_"))
async def process_sell_asset(callback_query: CallbackQuery, state: FSMContext):
    idx = int(callback_query.data.replace("sell_", ""))
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    asset = p['assets']['investments'][idx]
    await state.update_data(sell_idx=idx, sell_name=asset['name'], sell_price=asset['price'])
    await callback_query.message.edit_text(f"✍️ Сколько штук **{asset['name']}** продать? (У тебя {asset['qty']} шт.):")
    await state.set_state(CashflowStates.w_realize_qty)
    await callback_query.answer()


@dp.message(CashflowStates.w_realize_qty)
async def process_sell_qty(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    qty = int(message.text)
    data = await state.get_data()
    idx = data['sell_idx']
    user_id = message.from_user.id
    p = get_player(user_id)
    if qty <= 0 or qty > p['assets']['investments'][idx]['qty']:
        await message.answer("❌ Неверное количество.")
        await state.clear()
        return
    cash_gain = data['sell_price'] * qty
    p['cash'] += cash_gain
    p['assets']['investments'][idx]['qty'] -= qty
    if p['assets']['investments'][idx]['qty'] == 0:
        del p['assets']['investments'][idx]
    update_player(user_id, p)
    await message.answer(f"✅ Продано {qty} шт. {data['sell_name']} за ${cash_gain}!", reply_markup=get_inner_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "buy_asset")
async def start_buy_asset(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("✍️ Введите **название** актива:", parse_mode="Markdown")
    await state.set_state(CashflowStates.w_asset_name)
    await callback_query.answer()


@dp.message(CashflowStates.w_asset_name)
async def process_a_name(message: types.Message, state: FSMContext):
    await state.update_data(a_name=message.text)
    await message.answer("🏷️ Введите **тип** (Акции, Недвижимость, Бизнес, Облигации, Другое):")
    await state.set_state(CashflowStates.w_asset_type)


@dp.message(CashflowStates.w_asset_type)
async def process_a_type(message: types.Message, state: FSMContext):
    await state.update_data(a_type=message.text)
    await message.answer("💰 Введите **цену за 1 штуку**:")
    await state.set_state(CashflowStates.w_asset_price)


@dp.message(CashflowStates.w_asset_price)
async def process_a_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
    else:
        await state.update_data(a_price=int(message.text))
        await message.answer("📈 Введите **доход за 1 штуку** за круг:")
        await state.set_state(CashflowStates.w_asset_income)


@dp.message(CashflowStates.w_asset_income)
async def process_a_income(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
    else:
        await state.update_data(a_income=int(message.text))
        await message.answer("🔢 Введите **количество** штук для покупки:")
        await state.set_state(CashflowStates.w_asset_qty)


@dp.message(CashflowStates.w_asset_qty)
async def process_a_qty(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    data = await state.get_data()
    total_cost = data['a_price'] * int(message.text)
    user_id = message.from_user.id
    p = get_player(user_id)
    if p['cash'] < total_cost:
        await message.answer(f"❌ Не хватает денег! Нужно ${total_cost}.")
        await state.clear()
        return
    p['cash'] -= total_cost
    p['assets']['investments'].append(
        {"name": data['a_name'], "type": data['a_type'], "price": data['a_price'], "income": data['a_income'],
         "qty": int(message.text)})
    update_player(user_id, p)
    await message.answer(
        f"✅ {data['a_name']} куплен! -${total_cost}. Доход +${data['a_income'] * int(message.text)}/круг.",
        parse_mode="Markdown", reply_markup=get_inner_keyboard())
    await state.clear()


# --- ДЕЙСТВИЯ НА ПОЛЕ ---
@dp.callback_query(lambda c: c.data == "field_action")
async def process_field_action(callback_query: CallbackQuery):
    kb = [[types.InlineKeyboardButton(text="📉 Увольнение", callback_data="ev_fire")],
          [types.InlineKeyboardButton(text="🎁 Благотворительность", callback_data="ev_charity")],
          [types.InlineKeyboardButton(text="🛒 Безделушки", callback_data="ev_junk")],
          [types.InlineKeyboardButton(text="💸 Выплатить долги", callback_data="pay_liability")],
          [types.InlineKeyboardButton(text="🔙 Назад", callback_data="profile")]]
    await callback_query.message.edit_text("⚡ Выбери событие на поле:",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "ev_fire")
async def ev_fire(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    ti, te, cf, pi, bi = calculate_finances(p)
    await callback_query.message.edit_text(f"📉 Увольнение! Твой общий доход: ${ti}.\nСколько спишешь с наличных?")
    await state.set_state(CashflowStates.w_event_fire)
    await callback_query.answer()


@dp.message(CashflowStates.w_event_fire)
async def ev_fire_apply(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    user_id = message.from_user.id
    p = get_player(user_id)
    amount = min(int(message.text), p['cash'])
    p['cash'] -= amount
    update_player(user_id, p)
    await message.answer(f"📉 Оплачено ${amount}. Пропусти 2 хода!", reply_markup=get_inner_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "ev_charity")
async def ev_charity(callback_query: CallbackQuery, state: FSMContext):
    ti, te, cf, pi, bi = calculate_finances(get_player(callback_query.from_user.id))
    # Создаем клавиатуру с кнопкой Назад
    kb = [
        [types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    await callback_query.message.edit_text(
        f"🎁 Благотворительность. Твой общий доход: ${ti}.\nВведи сумму пожертвования:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.set_state(CashflowStates.w_event_charity)
    await callback_query.answer()

@dp.message(CashflowStates.w_event_charity)
async def ev_charity_apply(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    user_id = message.from_user.id
    p = get_player(user_id)
    amount = min(int(message.text), p['cash'])
    p['cash'] -= amount
    update_player(user_id, p)
    await message.answer(f"🎁 Пожертвовано ${amount}! Кидай 2 кубика 3 раза! 🎲", reply_markup=get_inner_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "ev_junk")
async def ev_junk(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("🛒 Безделушки. Введи сумму обязательной покупки:")
    await state.set_state(CashflowStates.w_event_junk)
    await callback_query.answer()


@dp.message(CashflowStates.w_event_junk)
async def ev_junk_apply(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    user_id = message.from_user.id
    p = get_player(user_id)
    amount = min(int(message.text), p['cash'])
    p['cash'] -= amount
    update_player(user_id, p)
    await message.answer(f"🛒 Потрачено ${amount} на безделушки!", reply_markup=get_inner_keyboard())
    await state.clear()


# --- КОРРЕКТИРОВКА НАЛИЧНЫХ ---
@dp.callback_query(lambda c: c.data == "adjust_cash")
async def process_adjust_cash(callback_query: CallbackQuery):
    kb = [[types.InlineKeyboardButton(text="➕ Пополнить", callback_data="add_cash")],
          [types.InlineKeyboardButton(text="➖ Снять", callback_data="sub_cash")],
          [types.InlineKeyboardButton(text="🔙 Назад", callback_data="profile")]]
    await callback_query.message.edit_text("💵 Регулировка наличных:",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "add_cash")
async def add_cash_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("➕ Введите сумму для пополнения:")
    await state.set_state(CashflowStates.w_add_cash)
    await callback_query.answer()


@dp.message(CashflowStates.w_add_cash)
async def add_cash_apply(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    user_id = message.from_user.id
    p = get_player(user_id)
    p['cash'] += int(message.text)
    update_player(user_id, p)
    await message.answer(f"➕ Баланс пополнен на ${message.text}!", reply_markup=get_inner_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "sub_cash")
async def sub_cash_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("➖ Введите сумму для списания:")
    await state.set_state(CashflowStates.w_sub_cash)
    await callback_query.answer()


@dp.message(CashflowStates.w_sub_cash)
async def sub_cash_apply(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    user_id = message.from_user.id
    p = get_player(user_id)
    amount = min(int(message.text), p['cash'])
    p['cash'] -= amount
    update_player(user_id, p)
    await message.answer(f"➖ Списано ${amount}!", reply_markup=get_inner_keyboard())
    await state.clear()


# --- ВНЕШНИЙ КРУГ (БАЗОВЫЙ КАРКАС) ---
@dp.callback_query(lambda c: c.data == "realize_business")
async def process_realize_business(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("📈 Введите название продаваемого бизнеса:")
    await state.set_state(CashflowStates.w_realize_name)
    await callback_query.answer()


@dp.message(CashflowStates.w_realize_name)
async def realize_name(message: types.Message, state: FSMContext):
    await state.update_data(r_name=message.text)
    await message.answer("💰 Введите сумму, полученную за продажу:")
    await state.set_state(CashflowStates.w_realize_qty)


@dp.message(CashflowStates.w_realize_qty)
async def realize_value(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    data = await state.get_data()
    user_id = message.from_user.id
    p = get_player(user_id)
    p['cash'] += int(message.text)
    update_player(user_id, p)
    await message.answer(f"💼 {data['r_name']} продан за ${message.text}!", reply_markup=get_outer_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "buy_outer_asset")
async def start_buy_outer(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("✍️ Введите название бизнеса:")
    await state.set_state(CashflowStates.w_outer_name)
    await callback_query.answer()


@dp.message(CashflowStates.w_outer_name)
async def process_out_name(message: types.Message, state: FSMContext):
    await state.update_data(o_name=message.text)
    await message.answer("💰 Введите стоимость:")
    await state.set_state(CashflowStates.w_outer_cost)


@dp.message(CashflowStates.w_outer_cost)
async def process_out_cost(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    await state.update_data(o_cost=int(message.text))
    await message.answer("📈 Введите доход в месяц:")
    await state.set_state(CashflowStates.w_outer_income)


@dp.message(CashflowStates.w_outer_income)
async def process_out_inc(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    await state.update_data(o_inc=int(message.text))
    await message.answer("📉 Введите ежемесячный расход бизнеса:")
    await state.set_state(CashflowStates.w_outer_expense)


@dp.message(CashflowStates.w_outer_expense)
async def process_out_exp(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число.")
        return
    data = await state.get_data()
    user_id = message.from_user.id
    p = get_player(user_id)
    if p['cash'] < data['o_cost']:
        await message.answer(f"❌ Не хватает денег! Нужно ${data['o_cost']}.")
        await state.clear()
        return
    p['cash'] -= data['o_cost']
    p['outer_assets'].append(
        {"name": data['o_name'], "cost": data['o_cost'], "income": data['o_inc'], "monthly_expense": int(message.text)})
    update_player(user_id, p)
    await message.answer(f"✅ Бизнес **{data['o_name']}** куплен!", reply_markup=get_outer_keyboard())
    await state.clear()


@dp.callback_query(lambda c: c.data == "exit_game")
async def process_exit_game(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    if p['game_phase'] != "outer":
        await callback_query.answer("Ты еще в Крысиных бегах!", show_alert=True)
        return
    outer_passive_income = sum(a['income'] - a['monthly_expense'] for a in p['outer_assets'])
    victory_score = p['cash'] + (outer_passive_income * 12)
    await callback_query.message.edit_text(
        f"🏁 **ПОБЕДА!**\n\nИтоговый капитал: ${p['cash']}\nФинальный счет: ${victory_score}",
        parse_mode="Markdown"
    )
    await callback_query.answer()

# --- ОБРАБОТЧИК КНОПКИ "НАЗАД В МЕНЮ" ---
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def process_back_to_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    p = get_player(user_id)
    # Очищаем состояние, если вдруг игрок был в диалоге
    # Просто показываем профиль (или главное меню)
    await process_profile(callback_query)

# --- БУДИЛЬНИК И ЗАПУСК ---
import asyncio

async def send_keep_alive():
    """Стабильный будильник для Render: просто спит, ничего не отправляет"""
    while True:
        await asyncio.sleep(40)  # Просыпаемся каждые 40 секунд

async def main():
    # 1. Запускаем веб-сервер (чтобы Render не ругался)
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=10000)
    await site.start()
    
    # 2. Запускаем будильник в фоне (он будет тихо тикать 24/7)
    asyncio.create_task(send_keep_alive())
    
    print("✅ Веб-заглушка и будильник запущены. Бот стартует...")
    
    # 3. Запускаем самого бота
    await dp.start_polling(bot)

# --- СБРОС ИГРЫ ---
@dp.callback_query(lambda c: c.data == "reset_game")
async def process_reset_game(callback_query: CallbackQuery):
    # Спрашиваем подтверждение, чтобы не стереть всё случайно
    kb = [
        [types.InlineKeyboardButton(text="✅ Да, сбросить всё!", callback_data="reset_confirm")],
        [types.InlineKeyboardButton(text="❌ Нет, отмена", callback_data="profile")]
    ]
    await callback_query.message.edit_text(
        "⚠️ **Внимание! Ты уверен, что хочешь завершить игру и стереть весь прогресс?**\n"
        "Это действие удалит данные ВСЕХ игроков (баланс, активы, профессии).",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "reset_confirm")
async def process_reset_confirm(callback_query: CallbackQuery):
    # Полностью очищаем файл данных
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write('{}')  # Записываем пустой JSON
    
    await callback_query.message.edit_text(
        "🗑️ **Игра завершена! Все данные стерты.**\n"
        "Теперь вы можете нажать /start, чтобы начать новую игру с нуля.",
        parse_mode="Markdown"
    )
    await callback_query.answer()
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
