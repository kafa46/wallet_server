from typing import Dict
from html_sanitizer import Sanitizer

def sanitizer(html_string: str = None) -> str:
    '''HTML sanitizer'''
    sani = Sanitizer()
    # 정수 혹은 실수 데이터일 경우 그대로 리턴
    if isinstance(html_string, int) or isinstance(html_string, float) :
        return html_string
    # 문자열일 경우 sanitize 수행
    if html_string:
        html_string = sani.sanitize(html_string)
        return html_string
    # 값이 없을 경우 그대로 리턴
    return html_string


def sanitize_json_or_dict(request_json: Dict[str, str] = None) -> Dict[str, any]:
    '''Sanitize request.json or Dict -> return sanitized Dict'''
    sanitized_dic = {
        k: sanitizer(v) for k, v in request_json.items()
    }
    return sanitized_dic