import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Function to load questions from a text file
def load_questions(file_path):
    questions = []
    with open(file_path, 'r') as file:
        content = file.read().strip().split('\n\n')  # Split questions based on double newlines
        for block in content:
            lines = block.strip().split('\n')
            question = lines[0]
            options = lines[1:5]

            # Extract the answer from the last line
            answer_match = re.search(r'Ans \[(\w)', lines[5]) if len(lines) > 5 else None
            if answer_match:
                answer = answer_match.group(1).lower()  # Store answer in lowercase for comparison
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
            else:
                print(f"Warning: No valid answer found for question: {question}")

    return questions

# Load questions
questions = load_questions('mcqs.txt')

user_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Quiz Bot! Use /quiz to start.")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_scores[user_id] = {"score": 0, "current_question": 0}
    await send_question(user_id, update.message.chat.id, context)

async def send_question(user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_question = user_scores[user_id]["current_question"]

    if current_question < len(questions):
        question = questions[current_question]
        options = question["options"]

        # Create a keyboard with options
        keyboard = []
        for option in options:
            button_label = option  # Keep the full option as label
            keyboard.append([InlineKeyboardButton(button_label, callback_data=option[0])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=question["question"], reply_markup=reply_markup)
    else:
        await finish_quiz(user_id, chat_id, context)

async def finish_quiz(user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    score = user_scores[user_id]["score"]
    await context.bot.send_message(chat_id=chat_id, text=f"Quiz finished! Your score: {score}/{len(questions)}")
    del user_scores[user_id]

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    answer = update.callback_query.data.lower()  # Convert answer to lowercase
    current_question = user_scores[user_id]["current_question"]

    # Check if the answer is correct
    if answer == questions[current_question]["answer"]:
        user_scores[user_id]["score"] += 1

    # Move to the next question
    user_scores[user_id]["current_question"] += 1
    await send_question(user_id, update.callback_query.message.chat.id, context)

def main():
    # Replace 'YOUR_TOKEN' with your bot's token
    application = ApplicationBuilder().token("6021389865:AAFJX5pxPCVvJ-1GT2blj3jCRDffbDqenV0").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
