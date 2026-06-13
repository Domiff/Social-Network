from http.cookies import SimpleCookie


def get_refresh_token(response):
    set_cookie = response.headers.get("set-cookie")
    cookie = SimpleCookie()
    cookie.load(set_cookie)
    return cookie["refresh_token"].value
