from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gitlab_url: str
    gitlab_private_token: str
    gitlab_project_id: int
    openai_api_key: str
    slack_token: str
    slack_signing_secret: str
    slack_channel_id: str
    port:int = 3000

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
