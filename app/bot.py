# from app.chat_bot import groq_chat_bot_response
import discord
from discord.ext import commands, tasks
from app.models import *
from datetime import datetime, timedelta
from os import getenv
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = getenv("DISCORD_TOKEN", "")
PREFIX = "/"


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = False


bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    check_expirations.start()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("/"):
        await bot.process_commands(message)  # ainda deixa o comando funcionar
        return

    # if message.channel.id in [1416465529358778468]:
    #     to_response = await groq_chat_bot_response(message.content)
    #     await message.channel.send(f'{message.author.mention}' + to_response)

    if not DiscordUser.has_user(message.author.id):
        create_discord_user(message.author)

    if message.author.id in [1286014015847403671] and message.channel.id in [1415059789599211520]:
        img_url = None
        if message.attachments:
            img_url = message.attachments[0].url

        PendingMessage.create(content=message.content or None, image_url=img_url, created_at=datetime.now())
        print(f"Mensagem salva: {message.content} {img_url}")


@bot.command()
async def validar(ctx):
    if ctx.message:
        raw_privacy_user, code = ctx.message.content.split(' ')[1].split('-')
        privacy_user = PrivacyUser.has_user(raw_privacy_user)
        code_privacy = CodePrivacy.has_code(code, privacy_user)
        if privacy_user and code_privacy:
            discord_user = get_discord_user(ctx.author, privacy_user)
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="VIP Discord"))
            code_privacy.delete_instance()
            await ctx.send(f"{ctx.author.mention} Você foi validado com sucesso! Seja Bem-Vindo ao nosso cantinho")
        else:
            await ctx.send(f"{ctx.author.mention} Código ou Assinante Inválido!")
        await ctx.message.delete()


@bot.command()
@commands.has_permissions(manage_roles=True)
async def generate(ctx):
    if ctx.message:
        raw_privacy_user, expires_days = ctx.message.content.split(' ')[1].split('-')
        privacy_user = get_privacy_user(raw_privacy_user, expires_days)
        code_privacy = create_code(privacy_user, expires_days)
        await ctx.send(f'''{ctx.author.mention} Código Criado com Sucesso!\n\n\n
                        {privacy_user.create_privacy_welcome_message(code_privacy.code_id)}''')


@bot.command()
@commands.has_permissions(manage_roles=True)  # só quem tem permissão pode usar
async def cargo(ctx, member: discord.Member, role: discord.Role):
    """Atribui um cargo a um usuário. Ex: !cargo @fulano @VIP"""
    try:
        await member.add_roles(role)
        await ctx.send(f"✅ Cargo {role.name} adicionado a {member.mention}")
    except discord.Forbidden:
        await ctx.send("🚫 Não tenho permissão para gerenciar esse cargo.")
    except Exception as e:
        await ctx.send(f"⚠️ Erro: {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removecargo(ctx, member: discord.Member, role: discord.Role):
    """Remove um cargo de um usuário. Ex: !removecargo @fulano @VIP"""
    try:
        await member.remove_roles(role)
        await ctx.send(f"❌ Cargo {role.name} removido de {member.mention}")
    except discord.Forbidden:
        await ctx.send("🚫 Não tenho permissão para gerenciar esse cargo.")
    except Exception as e:
        await ctx.send(f"⚠️ Erro: {e}")


@tasks.loop(minutes=10)
async def check_expirations():
    expired_users = (
                    DiscordUser
                    .select()
                    .join(PrivacyUser, on=(DiscordUser.privacy_user == PrivacyUser.privacy_id))
                    .where(PrivacyUser.expire_on < datetime.now())
                    )

    for user in expired_users:
        guild = discord.utils.get(bot.guilds)  # se o bot só estiver em 1 servidor
        member = guild.get_member(int(user.discord_id))
        if member:
            role = discord.utils.get(guild.roles, name='VIP Discord')
            if role in member.roles:
                await member.remove_roles(role)
                print(f"🚫 Cargo {role.name} removido de {member.display_name}")
        privacy_user = user.privacy_user
        privacy_user.expire_on = None
        privacy_user.save()


def get_discord_user(author, privacy_user):
    discord_user = DiscordUser.has_user(author.id)
    if discord_user:
        return discord_user
    return create_discord_user(author, privacy_user)


def create_discord_user(author, privacy_user=None):
    discord_user = DiscordUser()
    discord_user.created_at = datetime.now()
    discord_user.discord_name = author.name
    discord_user.privacy_user = privacy_user
    discord_user.discord_id = author.id
    discord_user.save(force_insert=True)
    return discord_user


def get_privacy_user(raw_privacy_user, expires_days):
    privacy_user = PrivacyUser.has_user(raw_privacy_user)
    if privacy_user:
        privacy_user.expire_on = datetime.now() + timedelta(days=int(expires_days))
        privacy_user.updated_at = datetime.now()
        privacy_user.save()
        return privacy_user
    privacy_user = PrivacyUser()
    privacy_user.privacy_name = raw_privacy_user
    privacy_user.expire_on = datetime.now() + timedelta(days=int(expires_days))
    privacy_user.created_at = datetime.now()
    privacy_user.save(force_insert=True)
    return privacy_user


def create_code(privacy_user, expires_days):
    code_privacy = CodePrivacy.has_privacy_code(privacy_user)
    if not code_privacy:
        code_privacy = CodePrivacy()
        code_privacy.privacy_user = privacy_user
        code_privacy.generate_unique_hash()
        code_privacy.expire_on = datetime.now() + timedelta(days=int(expires_days))
        privacy_user.expire_on = code_privacy.expire_on
        code_privacy.created_at = datetime.now()
        code_privacy.save(force_insert=True)
    return code_privacy


if __name__ == '__main__':
    bot.run(TOKEN)
