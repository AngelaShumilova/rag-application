from telegram.ext import *
import utils

if __name__ == '__main__':
    import sys

    try:
        print('Bro is high and running')
        # Build the application
        application = Application.builder().token(utils.token).build()
        # Match predefined functions to chat input
        # start command (command handler)
        application.add_handler(CommandHandler('start', utils.start_command))
        application.add_handler(CallbackQueryHandler(utils.button_tap))
        # AI assistant command (message handler)
        application.add_handler(MessageHandler(filters.TEXT, utils.AI_assistant_command_handler))
        # Filter unwanted commands
        application.add_handler(MessageHandler(filters.COMMAND, utils.unrecognized_command))
        # Handle errors
        application.add_error_handler(utils.error_handler)
        # Run bot
        application.run_polling(1.0)
    except KeyboardInterrupt:
        sys.exit(0)
