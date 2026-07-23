import os
import discord
from discord import app_commands
from discord_ver.auth_dc import LoginModel
from discord.ext import tasks
import httpx


ENDPOINT = os.environ.get("ENDPOINT")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Save DB but next step
linked_users: dict[int, str] = {}

hold_task = {}

# Departure management(時間管理, 通知)
@client.event
async def departures(interaction: discord.Interaction):
    pass

# Authentication
@tree.command(name="auth", description="認証を行います.")
async def auth(interaction: discord.Interaction):
    await interaction.response.send_modal(LoginModel())

# Show schedule list
@tree.command(name="list", description="📅 予定の一覧を表示します.")
async def lists(interaction: discord.Interaction, api_key: str):
    async with httpx.AsyncClient() as http:
        get_list = await http.get(f"{ENDPOINT}/task/", headers={"Authorization": f"bearer {api_key}"})
        if get_list.status_code != 200:
            await interaction.response.send_message("予定を取得できませんでした...", ephemeral=True)
            return
        list_data = get_list.json()
    list_message = "\n".join([f"{task['id']}: {task['plan_name']}" for task in list_data])
    await interaction.response.send_message(list_message, ephemeral=True)
    return

# Show schedule details
@tree.command(name="details", description="📅 予定の詳細を表示します.")
async def details(interaction: discord.Interaction, api_key: str, plan_name: str):
    async with httpx.AsyncClient() as http:
        task_id = await http.get(f"{ENDPOINT}/task/nti", params={"plan_name": plan_name}, headers={"Authorization": f"bearer {api_key}"}).json()
        get_detail = await http.get(f"{ENDPOINT}/task/view_task", params={"task_id": task_id}, headers={"Authorization": f"bearer {api_key}"})
        if get_detail.status_code != 200:
            await interaction.response.send_message("予定を表示できませんでした...", ephemeral=True)
            return
        detail = get_detail.json()
    struct_detail = "\n".join(f"{key}: {value}" for key, value in detail.items())
    await interaction.response.send_message(struct_detail, ephemeral=True)
    return

# Create a schedule
@tree.command(name="add", description="✏️ 予定を新規作成します. /acceptで確定します.")
async def add(interaction: discord.Interaction, api_key: str, tasks: str):
    async with httpx.AsyncClient() as http:
        send_task = await http.post(f"{ENDPOINT}/prompt_ctl/prompt_analyze", params={"prompt": tasks}, headers={"Authorization": f"bearer {api_key}"})
        if send_task.status_code != 200:
            await interaction.response.send_message("予定を作成できませんでした...", ephemeral=True)
            return
        global hold_task
        hold_task = send_task.json()
    await interaction.response.send_message(f"以下のタスクを登録するには, /accept -all または {hold_task}", ephemeral=True)
    return

# Accept and regist schedule
@tree.command(name="accept", description="✏️ 予定を確定します.")
async def accept(interaction: discord.Interaction, api_key: str, option: str):
    async with httpx.AsyncClient() as http:
        if option == "-all":
            accept_all = await http.post(f"{ENDPOINT}/task/add", json=hold_task, headers={"Authorization": f"bearer {api_key}"})
            if accept_all.status_code != 200:
                await interaction.response.send_message("予定を登録できませんでした....", ephemeral=True)
                return
            await interaction.response.send_message("全ての予定を登録しました!!", ephemeral=True)
        else:
            accept_one = await http.post(f"{ENDPOINT}/task/add", json=hold_task, headers={"Authorization": f"bearer {api_key}"})
            if accept_one.status_code != 200:
                await interaction.response.send_message("予定を登録できませんでした....", ephemeral=True)
                return
            await interaction.response.send_message("1つの予定を登録しました!!", ephemeral=True)

# Edit a schedule
@tree.command(name="edit", description="🖋 予定の編集を行います.")
async def edit(interaction: discord.Interaction, api_key: str, plan_name: str):
    async with httpx.AsyncClient() as http:
        task_id = await http.get(f"{ENDPOINT}/task/nti", params={"plan_name": plan_name}, headers={"Authorization": f"bearer {api_key}"}).json()
        get_task = await http.get(f"{ENDPOINT}/task/view_task", params={"task_id": task_id}, headers={"Authorization": f"bearer {api_key}"})
        if get_task.status_code != 200:
            await interaction.response.send_message("予定を変更できませんでした.", ephemeral=True)
            return
        task_data = get_task.json()
        edit_task = await http.post(f"{ENDPOINT}/task/edit_task", params={"task_id": task_data["task_id"]}, headers={"Authorization": f"bearer {api_key}"})
        if edit_task.status_code != 200:
            await interaction.response.send_message("予定を変更できませんでした.", ephemeral=True)
            return
        await interaction.response.send_message(f"予定を変更しました. {plan_name}", ephemeral=True)
    return

# Delete a schedule
@tree.command(name="del", description="🗑 予定の削除を行います.")
async def remove(interaction: discord.Interaction, api_key: str, plan_name: str):
    async with httpx.AsyncClient() as http:
        task_id = await http.get(f"{ENDPOINT}/task/nti", params={"plan_name": plan_name}, headers={"Authorization": f"bearer {api_key}"}).json()
        delete_task = await http.get(f"{ENDPOINT}/task/delete_task", params={"task_id": task_id}, headers={"Authorization": f"bearer {api_key}"})
        if delete_task.status_code != 200:
            await interaction.response.send_message("予定を削除できませんでした...", ephemeral=True)
            return
    await interaction.response.send_message(f"予定を削除しました. 結果：{delete_task}", ephemeral=True)
    return

# Departure
@tasks.loop(minutes=1)
async def check_departures():
    async with httpx.AsyncClient() as http:
        for discord_id, api_key in list(linked_users.items()):
            res = await http.get(f"{ENDPOINT}/task/departure", headers={"Authenticated": f"bearer {api_key}"})
            if res.status != 200:
                continue
            due_list = res.json()
            if not due_list:
                continue
            user = client.get_user(discord_id) or await client.fetch_user(discord_id)
            for task in due_list:
                await user.send(f"そろそろ出発の時間だー！！ 「{task['plan_name']}」準備OK?")
                await http.post(f"{ENDPOINT}/task/departure/{task['id']/ack}", headers={"Authenticated": f"bearer {api_key}"})


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await tree.sync()
    check_departures.start()

client.run(BOT_TOKEN)
