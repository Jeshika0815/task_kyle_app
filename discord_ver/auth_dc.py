import discord
import httpx
import main
import os

ENDPOINT = os.environ.get("ENDPOINT")

class LoginModel(discord.ui.Modal, title="ログイン"):
    email = discord.ui.TextInput(label="Email")
    password = discord.ui.TextInput(label="Password")

    async def on_submit(self, interaction: discord.Interaction):
        async with httpx.AsyncClient() as http:
            login_res = await http.post(f"{ENDPOINT}/auth/login", json={"username": self.email, "password": self.password})
            if login_res.status_code != 200:
                await interaction.response.send_message("ログインに失敗しました", ephemeral=True)
                return
            jwt_token = login_res.json()["access_token"]

            # JWT token is short-lived so generate a long-lived api key
            key_res = await http.post(f"{ENDPOINT}/auth/bot_token", headers={"Authorization": f"Bearer {jwt_token}"})
            if key_res.status_code != 200:
                await interaction.response.send_message("APIキーの発行に失敗しました", ephemeral=True)
                return
            api_key = key_res.json()["api_key"]

        save_link_user(interaction.user.id, api_key)
        await interaction.response.send_message("ログインと連携が完了いたしました.", ephemeral=True)

def save_link_user(user_id: int, api_key: str):
    main.linked_users[user_id] = api_key
