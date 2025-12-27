from pathlib import Path
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic_settings import BaseSettings, YamlConfigSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict, InitSettingsSource
from pydantic.alias_generators import to_pascal

class BaseComponent(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        validate_by_name=True,
        validate_by_alias=True
    )

class BaseConfig(BaseSettings):

    yaml_path: str | Path | None = None

    model_config = SettingsConfigDict(
        alias_generator=to_pascal,
        # env things
        env_prefix = '',
        env_nested_delimiter='__',
        nested_model_default_partial_update=True,
        extra='ignore',
        validate_by_name=True,
        validate_by_alias=True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:

        return (
            init_settings,
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=cls.yaml_path,
                yaml_file_encoding="utf-8"
            ),
            env_settings,
            dotenv_settings,
            file_secret_settings
        )

    @classmethod
    def from_yaml(cls, yaml_path: str | Path):
        cls.yaml_path = yaml_path
        return cls()