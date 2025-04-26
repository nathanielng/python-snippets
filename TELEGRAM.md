# TELEGRAM

## 1. Creating a new Telegram bot

1. Go to https://web.telegram.org/k/#@BotFather
2. Create a new bot with `/newbot`
3. Type in a name for the bot: `your_bot_name`
4. Save the Telegram API token
5. [Optional] View the bot with `/mybots` and set the Botpic (minimum dimensions: 150 x 150)

## 2. Starting the bot and obtaining the Chat ID

1. Navigate to https://t.me/your_bot_name and click **Start Bot**. Type `/start` and type your first message, such as "Hi"
2. Paste the following link in your browser: https://api.telegram.org/botTELEGRAM_API_TOKEN/getUpdates (replace `TELEGRAM_API_TOKEN`, with your actual API token)
   You can also run `curl https://api.telegram.org/botTELEGRAM_API_TOKEN/getUpdates` in a terminal window.
3. In the response, look for the `id` field, e.g. `{"id":1234567,...`. The numeric digits after `id` will be your Chat ID.

## 3. Setting a webhook URL

Paste the following in a browser: https://api.telegram.org/botTELEGRAM_API_TOKEN/setWebhook?url=https://yourwebhookurl.
The response should show something like `{"ok":true,"result":true,"description":"Webhook was set"}`
