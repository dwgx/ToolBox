# utils/Translationcore.py

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models

SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ar": "Arabic",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "hi": "Hindi",
    "fa": "Persian",
}


def perform_translation(text, target_lang, config_manager, logger):
    secret_id = config_manager.get("translation", "SECRET_ID", "")
    secret_key = config_manager.get("translation", "SECRET_KEY", "")

    if not secret_id or not secret_key:
        logger.error("API密钥未设置。请通过设置界面输入并保存API密钥。")
        return "翻译错误: API密钥未设置。"

    if target_lang not in SUPPORTED_LANGUAGES:
        logger.error(f"不支持的目标语言代码: {target_lang}")
        return f"翻译错误: 不支持的目标语言代码 '{target_lang}'。"

    logger.info(f"开始翻译: '{text}'")
    try:
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "tmt.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = tmt_client.TmtClient(cred, "ap-guangzhou", client_profile)
        req = models.TextTranslateRequest()
        req.SourceText = text
        req.Source = "auto"
        req.Target = target_lang
        req.ProjectId = 0
        resp = client.TextTranslate(req)
        translation = resp.TargetText
        logger.info(f"翻译成功: '{translation}'")
        return translation
    except TencentCloudSDKException as e:
        logger.error(f"翻译错误: {str(e)}")
        return "翻译错误，请检查日志获取更多信息。"
    except Exception as e:
        logger.error(f"翻译错误: {str(e)}")
        return "翻译错误，请检查日志获取更多信息。"
