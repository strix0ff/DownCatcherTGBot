import asyncio

import aiohttp

import json

import aiofiles

from pathlib import ( 
    Path
)

from aiogram import (
    F,
    Router
)

from aiogram.filters import (
    CommandStart,
    StateFilter,
    BaseFilter
)

from aiogram.types import (
    Message,
    CallbackQuery,
    User
)

from aiogram.utils.keyboard import ( 
    InlineKeyboardBuilder
)

from aiogram.fsm.state import (
    State,
    StatesGroup
)

from aiogram.fsm.context import (
    FSMContext
)

from aiogram.methods import (
    VerifyUser
)

from bot.config import (
    ADMINID,
    APIKEY,
    APIPORT
)

router = Router()

class IsAdmin(BaseFilter):
    async def __call__(self, event, event_from_user: User):
        if event_from_user.id == int(ADMINID):
            return True
        return False

class AddService(StatesGroup):
    name = State()
    address = State()

lang_cfg_path = Path('lang.json')

CurLang = ''

service_id = ''

async def GetLangCfg():
    global CurLang
    if lang_cfg_path.is_file():
        async with aiofiles.open(lang_cfg_path, 'r', encoding='utf-8') as file:
            data = await file.read()
            data = json.loads(data)
            CurLang = data['lang']
    else:
        CurLang = 'en'

asyncio.run(GetLangCfg())

def GetMainKeyboard():
    builder = InlineKeyboardBuilder()
    if CurLang == 'en':
        btn_add_text = 'Add service'
        btn_del_text = 'Delete service'
        btn_get_text = 'Service list'
        btn_changelang_text = 'Change language'
    elif CurLang == 'ru':
        btn_add_text = 'Добавить сервис'
        btn_del_text = 'Удалить сервис'
        btn_get_text = 'Список сервисов'
        btn_changelang_text = 'Сменить язык'
    elif CurLang == 'fr':
        btn_add_text = 'Ajouter un service'
        btn_del_text = 'Supprimer un service'
        btn_get_text = 'Liste des services'
        btn_changelang_text = 'Changer de langue'
    elif CurLang == 'ch':
        btn_add_text = '添加服务'
        btn_del_text = '删除服务'
        btn_get_text = '服务列表'
        btn_changelang_text = '切换语言'

    builder.button(text=f'🆕 {btn_add_text}', callback_data='service_add')
    builder.button(text=f'❌ {btn_del_text}', callback_data='service_delete')
    builder.button(text=f'📋 {btn_get_text}', callback_data='service_getlist')
    builder.button(text=f'🌐 {btn_changelang_text}', callback_data='lang_change')
    builder.adjust(3)
    return builder.as_markup()

def GetCancelKeyboard():
    if CurLang == 'en':
        btn_menu_text = 'To menu'
    elif CurLang == 'ru':
       btn_menu_text = 'В меню'
    elif CurLang == 'fr':
       btn_menu_text = 'Retour au menu'
    elif CurLang == 'ch':
       btn_menu_text = '返回主菜单'

    builder = InlineKeyboardBuilder()
    builder.button(text=f'🏠 {btn_menu_text}', callback_data='cancel')
    return builder.as_markup()

def GetLangKeyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='🇬🇧 English', callback_data='lang_en')
    builder.button(text='🇷🇺 Русский', callback_data='lang_ru')
    builder.button(text='🇲🇫 Français', callback_data='lang_fr')
    builder.button(text='🇨🇳 中文', callback_data='lang_ch')
    builder.adjust(2)
    return builder.as_markup()

async def GetDeleteKeyboard():
    builder = InlineKeyboardBuilder()

    headers = {
        'X-API-Key': APIKEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api:{APIPORT}/service/get', headers=headers) as response:
            if response.status != 200:
                return

            response_data = await response.json()

    for v, k in response_data.items():
        builder.button(text=k['name'], callback_data=f'button_{v}')

    if CurLang == 'en':
        btn_menu_text = 'To menu'
    elif CurLang == 'ru':
       btn_menu_text = 'В меню'
    elif CurLang == 'fr':
       btn_menu_text = 'Retour au menu'
    elif CurLang == 'ch':
       btn_menu_text = '返回主菜单'

    builder.button(text=f'🏠 {btn_menu_text}', callback_data='cancel')
    builder.adjust(3)

    return builder.as_markup()


@router.callback_query(StateFilter('*'), F.data == 'cancel')
async def cancel_handler(c: CallbackQuery, state: FSMContext):
    await state.clear()
    if CurLang == 'en':
        await c.message.edit_text('<b>✅ You have returned to main menu</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
       await c.message.edit_text('<b>✅ Вы вернулись в меню</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await c.message.edit_text('<b>✅ Vous êtes de retour au menu</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch':
        await c.message.edit_text('<b>✅ 您已返回菜单</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')

@router.message(CommandStart(), IsAdmin())
async def start_handler(m: Message):
    if not lang_cfg_path.is_file():
        data = {
            "lang": 'en',
        }
    
        async with aiofiles.open(lang_cfg_path, 'w', encoding='utf-8') as file:

            lang = json.dumps(data, ensure_ascii=False, indent=4)

            await file.write(lang)
        await m.answer('<b>Please select desired language 🌐</b>', reply_markup=GetLangKeyboard(), parse_mode='HTML')
    else:
        if CurLang == 'en':
            await m.answer('<b>Hi there! Select the appropriate action 👇</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
        elif CurLang == 'ru':
            await m.answer('<b>Привет! Выбери нужное действие 👇</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
        elif CurLang == 'fr':
            await m.answer('<b>Bonjour ! Choisis une action 👇</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
        elif CurLang == 'ch':
            await m.answer('<b>你好！请选择下方操作 👇</b>', reply_markup=GetMainKeyboard(), parse_mode='HTML')

@router.callback_query(F.data == 'service_add', IsAdmin())
async def addservice_handler(c: CallbackQuery, state: FSMContext):
    if CurLang == 'en':
        await c.message.edit_text('Enter the service name 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
        await c.message.edit_text('Введите название сервиса 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await c.message.edit_text('Entrez le nom du service 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch': 
        await c.message.edit_text('请输入服务名称 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')

    await state.set_state(AddService.name)

@router.message(AddService.name)
async def add_name_service_handler(m: Message, state: FSMContext):
    if not isinstance(m.text, str):
        if CurLang == 'en':
            await m.answer('⚠️ The service name must be as text!', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'ru':
            await m.answer('⚠️ Название сервиса должно быть в виде текста!', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'fr':
            await m.answer('⚠️ Le nom du service doit être au format texte !', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'ch':
            await m.answer('⚠️ 服务名称必须是文本格式！', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        return

    await state.update_data(name=m.text)

    if CurLang == 'en':
        await m.answer('Enter the domain name/IP of service 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
        await m.answer('Введите домен/IP сервиса 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await m.answer("Entrez le domaine / l'IP du service 👇", reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch':
        await m.answer('请输入服务的域名/IP 👇', reply_markup=GetCancelKeyboard(), parse_mode='HTML')

    await state.set_state(AddService.address)

@router.message(AddService.address)
async def add_address_service_handler(m: Message, state: FSMContext):
    if not isinstance(m.text, str):
        if CurLang == 'en':
            await m.answer('⚠️ IP/Domain name must be as text!', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'ru':
            await m.answer('⚠️ IP/домен должен быть в виде текста!', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'fr':
            await m.answer("⚠️ L'IP / le domaine doit être au format texte !", reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        elif CurLang == 'ch':
            await m.answer('⚠️ IP/域名必须是文本格式！', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
        return

    data = await state.get_data()
    service_name = data.get('name')
    service_address = m.text

    payload = {
        'address': m.text,
        'name': service_name
    }

    headers = {
        'X-API-Key': APIKEY 
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://api:{APIPORT}/service/add', json=payload, headers=headers) as response:
            if response.status != 200:
                await m.answer(f'💀 API ERROR: <code>{response.status}</code>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
                await state.clear()
                return
    
    if CurLang == 'en':
        await m.answer(f'✅ Service <code>{service_name}</code> with address <code>{service_address}</code> has been successfully added!', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
        await m.answer(f'✅ Сервис <code>{service_name}</code> с адресом <code>{service_address}</code> успешно добавлен!', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await m.answer(f"✅ Le service <code>{service_name}</code> avec l'adresse <code>{service_address}</code> a été ajouté avec succès !", reply_markup=GetCancelKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch':
        await m.answer(f'✅ 地址为 <code>{service_address}</code> 的服务 <code>{service_name}</code> 已成功添加！', reply_markup=GetCancelKeyboard(), parse_mode='HTML')

    await state.clear()


@router.callback_query(F.data == 'service_delete', IsAdmin())
async def deleteservice_handler(c: CallbackQuery):
    if CurLang == 'en':
        await c.message.edit_text('Select a service to delete 👇', reply_markup=await GetDeleteKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
        await c.message.edit_text('Выберите сервис для удаления 👇', reply_markup=await GetDeleteKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await c.message.edit_text('Sélectionnez un service à supprimer 👇', reply_markup=await GetDeleteKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch':
        await c.message.edit_text('请选择要删除的服务 👇', reply_markup=await GetDeleteKeyboard(), parse_mode='HTML')      

@router.callback_query(F.data.startswith('button_'), IsAdmin())
async def delete_confirm_handler(c: CallbackQuery):

    global service_id

    builder = InlineKeyboardBuilder()

    if CurLang == 'en':
        btn_yes_text = 'Yes'
        btn_no_text = 'No'
        confirm_text = 'Are you sure?'
    elif CurLang == 'ru':
        btn_yes_text = 'Да'
        btn_no_text = 'Нет'
        confirm_text = 'Вы уверены?'
    elif CurLang == 'fr':
        btn_yes_text = 'Confirmer'
        btn_no_text = 'Annuler'
        confirm_text = 'Êtes-vous sûr ?'
    elif CurLang == 'ch':
        btn_yes_text = '确定'
        btn_no_text = '取消'
        confirm_text = '您确定吗？'


    builder.button(text=f'✅ {btn_yes_text}', callback_data='delete_confirm')
    builder.button(text=f'❌ {btn_no_text}', callback_data='cancel')

    keylist = c.data.split('_')
    service_id = keylist[1]

    await c.message.edit_text(f'<b>{confirm_text}</b>', reply_markup=builder.as_markup(), parse_mode='HTML')

@router.callback_query(F.data == 'delete_confirm', IsAdmin())
async def delete_end_handler(c: CallbackQuery):

    global service_id

    headers = {
        'X-API-Key': APIKEY 
    }

    
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'http://api:{APIPORT}/service/{service_id}', headers=headers) as response:
            if response.status != 200:
                await c.message.edit_text(f'💀 API ERROR: <code>{response.status}</code>', reply_markup=GetMainKeyboard(), parse_mode='HTML')
                service_id = ''
                return

    service_id = ''

    if CurLang == 'en':
        await c.message.edit_text('✅ Service has been deleted!', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'ru':
        await c.message.edit_text('✅ Сервис был удалён!', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'fr':
        await c.message.edit_text('✅ Le service a été supprimé !', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    elif CurLang == 'ch':
        await c.message.edit_text('✅ 服务已删除！', reply_markup=GetMainKeyboard(), parse_mode='HTML')



@router.callback_query(F.data == 'service_getlist', IsAdmin())
async def getservices_handler(c: CallbackQuery):

    headers = {
        'X-API-Key': APIKEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api:{APIPORT}/service/get', headers=headers) as response:
            if response.status != 200:
                await c.message.edit_text(f'💀 API ERROR: <code>{response.status}</code>', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
                return

            response_data = await response.json()

            if not response_data:
                if CurLang == 'en':
                    await c.message.edit_text('📋 The service list is empty', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
                elif CurLang == 'ru':
                    await c.message.edit_text('📋 Список сервисов пуст', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
                elif CurLang == 'fr':
                    await c.message.edit_text('📋 La liste des services est vide.', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
                elif CurLang == 'ch':
                    await c.message.edit_text('📋 服务列表为空', reply_markup=GetCancelKeyboard(), parse_mode='HTML')
                return

            if CurLang == 'en':
                list_name_text = 'Name: '
                list_address_text = 'Address: '
            elif CurLang == 'ru':
                list_name_text = 'Имя: '
                list_address_text = 'Адрес: '
            elif CurLang == 'fr':
                list_name_text = 'Nom : '
                list_address_text = 'Adresse : '
            elif CurLang == 'ch':
                list_name_text = '名称：'
                list_address_text = '地址：'

            final_text = ''

            for k in response_data.values():
                final_text += f'🏷️ {list_name_text}<code>{k["name"]}</code>\n'
                final_text += f'🔗 {list_address_text}<code>{k["address"]}</code>\n'
                final_text += f'-'*25
                final_text += f'\n'

    await c.message.edit_text(final_text, reply_markup=GetCancelKeyboard(), parse_mode='HTML')


# Lang

@router.callback_query(F.data == 'lang_change', IsAdmin())
async def lang_change_handler(c: CallbackQuery):
    await c.message.edit_text('<b>Please select desired language 🌐</b>\n', reply_markup=GetLangKeyboard(), parse_mode='HTML')

@router.callback_query(F.data == 'lang_en', IsAdmin())
async def lang_en_handler(c: CallbackQuery):
    async with aiofiles.open('lang.json', 'w', encoding='utf-8') as file:
        data = {
            "lang": 'en',
        }

        lang = json.dumps(data, ensure_ascii=False, indent=4)

        await file.write(lang)

        global CurLang
        CurLang = 'en'
    await c.message.edit_text('<b>English</b> selected ✅', reply_markup=GetMainKeyboard(), parse_mode='HTML')

@router.callback_query(F.data == 'lang_ru', IsAdmin())
async def lang_ru_handler(c: CallbackQuery):
    async with aiofiles.open('lang.json', 'w', encoding='utf-8') as file:
        data = {
            "lang": 'ru',
        }

        lang = json.dumps(data, ensure_ascii=False, indent=4)

        await file.write(lang)
        
        global CurLang
        CurLang = 'ru'
    await c.message.edit_text('Выбран <b>русский</b> ✅', reply_markup=GetMainKeyboard(), parse_mode='HTML')

@router.callback_query(F.data == 'lang_fr', IsAdmin())
async def lang_fr_handler(c: CallbackQuery):
    async with aiofiles.open('lang.json', 'w', encoding='utf-8') as file:
        data = {
            "lang": 'fr',
        }

        lang = json.dumps(data, ensure_ascii=False, indent=4)

        await file.write(lang)
        
        global CurLang
        CurLang = 'fr'
    await c.message.edit_text('<b>Français</b> sélectionné ✅', reply_markup=GetMainKeyboard(), parse_mode='HTML')

@router.callback_query(F.data == 'lang_ch', IsAdmin())
async def lang_ch_handler(c: CallbackQuery):
    async with aiofiles.open('lang.json', 'w', encoding='utf-8') as file:
        data = {
            "lang": 'ch',
        }

        lang = json.dumps(data, ensure_ascii=False, indent=4)

        await file.write(lang)
        
        global CurLang
        CurLang = 'ch'
    await c.message.edit_text('已选择<b>中文</b> ✅', reply_markup=GetMainKeyboard(), parse_mode='HTML')
    

