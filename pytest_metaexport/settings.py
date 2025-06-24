from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for pytest_metaexport.
    """

    project_title: str = ""

    max_cache_size: int = 10
    cache_dir: str = ".metaexport-cache"
    cache_name: str = "cache.json"

    css_path: str = "pytest_metaexport/static/style.css"
    template_path: str = "pytest_metaexport/static/default.html"

    generate_figures: bool = True

    class Config:
        env_prefix = "pytest_metaexport_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()  # type: ignore[call-arg]
