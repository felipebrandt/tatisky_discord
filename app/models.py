from datetime import datetime
from peewee import *
from db_connection import db
from utils import random_code


class BaseModel(Model):
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    class Meta:
        database = db


class PrivacyUser(BaseModel):
    privacy_id = AutoField(primary_key=True, help_text='Id do usuario')
    privacy_name = CharField(max_length=255, help_text='@')
    expire_on = DateField()

    def create_privacy_welcome_message(self, code):
        return f'''Bem-vindo(a)! Com sua assinatura você tem acesso ao meu grupo VIP no Discord. Se ainda não entrou, acesse tatisky.com.br e entre no grupo. Se já está no grupo, basta copiar e colar no chat: /validar {self.privacy_name}-{code}'''

    @staticmethod
    def has_user(username):
        user = PrivacyUser.select().where(PrivacyUser.privacy_name == username)
        if user:
            return user.get()
        return None


class TelegramUser(BaseModel):
    telegram_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    privacy_user = ForeignKeyField(PrivacyUser, to_field='privacy_id', null=True)
    name = CharField(max_length=255, help_text='Rua do Imóvel')


class DiscordUser(BaseModel):
    discord_id = BigIntegerField(primary_key=True, help_text='Id do endereço do Imóvel')
    discord_name = CharField(help_text='Id do endereço do Imóvel')
    privacy_user = ForeignKeyField(PrivacyUser, to_field='privacy_id', null=True)

    @staticmethod
    def has_user(username):
        user = DiscordUser.select().where(DiscordUser.discord_id==username)
        if user:
            return user.get()
        return None


class CodePrivacy(BaseModel):
    code_id = CharField(primary_key=True, help_text='Id do usuario')
    privacy_user = ForeignKeyField(PrivacyUser, to_field='privacy_id', null=True)
    expire_on = DateField()

    def generate_unique_hash(self):
        all_valid_cores = self.get_valid_codes()
        code = None
        while not code:
            random_string = random_code(6)
            if random_string not in all_valid_cores:
                code = random_string
        self.code_id = code

    @staticmethod
    def get_valid_codes():
        all_codes = []
        for code in CodePrivacy.select().where(CodePrivacy.expire_on <= datetime.now().date()):
            all_codes.append(code.code_id)
        return all_codes

    @staticmethod
    def has_code(code, privacy_user):
        user = CodePrivacy.select().where((CodePrivacy.code_id == code) & (CodePrivacy.privacy_user == privacy_user))
        if user:
            return user.get()
        return None

    @staticmethod
    def has_privacy_code(privacy_user):
        code = CodePrivacy.select().where(CodePrivacy.privacy_user == privacy_user)
        if code:
            return code.get()
        return None


if __name__ == '__main__':
    db.create_tables([PrivacyUser, DiscordUser, TelegramUser, CodePrivacy])


