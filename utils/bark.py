from urllib.parse import quote, urlparse, urlunparse

import requests

from utils.logger import setup_logger


logger = setup_logger()


def _normalize_bark_base_url(url):
    url = (url or "").strip()
    if not url:
        return ""

    if "{title}" in url or "{body}" in url:
        return url.rstrip("/")

    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if not parsed.scheme or not parsed.netloc or not path_parts:
        return url.rstrip("/")

    # 用户常复制 /key/这里改成推送内容 形式的地址；实际推送时只需要保留 key。
    key_path = "/" + path_parts[0]
    return urlunparse((parsed.scheme, parsed.netloc, key_path, "", "", "")).rstrip("/")


def send_bark_notification(bark_url, title, body):
    bark_url = _normalize_bark_base_url(bark_url)
    if not bark_url:
        logger.debug("未配置 Bark 推送地址，跳过通知")
        return False

    if "{title}" in bark_url or "{body}" in bark_url:
        url = bark_url.format(title=quote(title, safe=""), body=quote(body, safe=""))
    else:
        url = f"{bark_url}/{quote(title, safe='')}/{quote(body, safe='')}"

    try:
        response = requests.get(
            url,
            params={"group": "DouYinSparkFlow", "isArchive": "1"},
            timeout=10,
        )
        response.raise_for_status()
        logger.info("Bark 推送发送成功")
        return True
    except Exception as exc:
        logger.warning(f"Bark 推送发送失败: {exc}")
        return False
