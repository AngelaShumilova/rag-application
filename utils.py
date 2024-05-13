import logging

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from telegram.constants import ParseMode
from telegram.ext import *
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from langchain_community.vectorstores import FAISS

# инициируем модель
llm = Ollama(model='llama3', temperature=0)

# пишем промпт
template = '''Используй информацию ниже, чтобы ответить на вопрос в конце. Отвечай только на русском языке. Сделай 
ответ максимально полезным и менее формальным. {context} 
Question: {question} 
Helpful Answer:'''
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

embeddings = HuggingFaceEmbeddings()

vectordb = FAISS.load_local('faiss_index', embeddings, allow_dangerous_deserialization=True)
# создаём цепочку
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={'prompt': QA_CHAIN_PROMPT}
)

# %%

token = 'YOUR_TOKEN_HERE'

FIRST_MENU = '<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button.'
SECOND_MENU = '<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons.'

# Pre-assign button text
FIRST_BUTTON = 'Start'
FIRST_BUTTON_ID = 'button1'
SECOND_BUTTON = 'Расскажи про развитие навыков аудирования в начальной школе'
SECOND_BUTTON_ID = 'button2'
THIRD_BUTTON = 'Как эффективнее выучить английский к собеседованию?'
THIRD_BUTTON_ID = 'button3'

FIRST_MENU_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton(FIRST_BUTTON, callback_data=FIRST_BUTTON_ID)
]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(SECOND_BUTTON, callback_data=SECOND_BUTTON_ID)],
    [InlineKeyboardButton(THIRD_BUTTON, callback_data=THIRD_BUTTON_ID)]
])


async def menu(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    await context.bot.send_message(
        update.message.from_user.id,
        FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


async def start_command(update, context):
    await update.message.reply_text(
        text='Привет! Я бот, который поможет тебе найти ответы на вопросы по обучению иностранным языкам. Я могу быть '
             'полезным студентам педагогических направлений, практикующим специалистам и всем, кто интересуется '
             'обучением и изучением иностранных языков, а также научной деятельностью. Напиши мне свой вопрос.',
        reply_markup=SECOND_MENU_MARKUP,
    )


async def button_tap(update: Update, context: CallbackContext) -> None:
    """
    This handler processes the inline buttons on the menu
    """

    data = update.callback_query.data

    if data == FIRST_BUTTON_ID:
        await start_command(update, context)
    elif data == SECOND_BUTTON_ID:
        await AI_assistant_callback_query(SECOND_BUTTON, update, context)
    elif data == THIRD_BUTTON_ID:
        await AI_assistant_callback_query(THIRD_BUTTON, update, context)


# %%
async def unrecognized_command(update, context):
    text = update.message.text
    if not text.startswith('/start'):
        await update.message.reply_text(
            f'Не могу распознать команду:\n\"{text}\"\nПроверьте сообщение на ошибки и опечатки и попробуйте ещё раз.')
    else:
        pass


async def error_handler(update, context: CallbackContext) -> None:
    logger = logging.getLogger(__name__)

    logger.error('Exception while handling an update:', exc_info=context.error)

    await update.message.reply_text('Ошибка :( Перезапустите бота и попробуйте ещё раз.')


# %%


async def AI_assistant_command_handler(update, context):
    question = update.message.text
    await update.message.reply_text('Ищу информацию и генерирую ответ...')
    result = qa_chain({'query': question})
    # send the AI assistant response
    await update.message.reply_text(f'\n{result["result"]}\n')


async def AI_assistant_callback_query(question, update, context):
    query = update.callback_query

    await query.message.edit_text('Ищу информацию и генерирую ответ...')
    result = qa_chain({'query': question})
    # send the AI assistant response
    await query.message.edit_text(f'\n{result["result"]}\n')
