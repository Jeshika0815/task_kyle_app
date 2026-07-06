require("dotenv").config();

const { Client, GatewayIntentBits } = require("discord.js");
const axios = require("axios");

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.once("ready", () => {
  console.log(`Logged in as ${client.user.tag}`);
});

client.on("messageCreate", async (message) => {

  // Botは無視
  if (message.author.bot) return;

  // 指定チャンネル以外は無視
  if (message.channel.id !== process.env.CHANNEL_ID) return;

  try {

    const response = await axios.post(
      process.env.GAS_URL,
      {
        message: message.content,
        user: message.author.username
      }
    );

    await message.reply(response.data.reply);

  } catch (err) {
    console.error(err);
    await message.reply("Webhook通信エラー");
  }
});

client.login(process.env.TOKEN);
