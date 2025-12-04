import flet_audio as fa
import flet as ft
from navidrome import NavidromeAPI
import asyncio

from typing import List, Optional, Callable

import flet as ft
from typing import List, Optional, Callable

def show_banner(
    page: ft.Page,
    message: str,
    *,
    type: str = "info",  # "info" | "success" | "warning" | "error"
    actions: Optional[List[ft.Control]] = None,
    duration_ms: Optional[int] = None,
    leading_icon: Optional[str] = None,
    force_actions_below: bool = True,
) -> ft.Banner:
    # 🔍 自动判断当前主题
    is_dark = page.theme_mode == ft.ThemeMode.DARK

    # 🎨 颜色方案（明/暗双模式）
    # 注意：深色用 *500 主色* 作背景；浅色用 *50 柔光色* 作背景
    config = {
        "info": {
            "icon": ft.Icons.INFO_OUTLINED,
            "icon_color": ft.Colors.BLUE_400 if is_dark else ft.Colors.BLUE_600,
            "bgcolor_light": ft.Colors.BLUE_50,
            "bgcolor_dark": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_900),  # 半透深蓝
            "text_color": ft.Colors.BLUE_900 if not is_dark else ft.Colors.BLUE_100,
        },
        "success": {
            "icon": ft.Icons.CHECK_CIRCLE_OUTLINED,
            "icon_color": ft.Colors.GREEN_400 if is_dark else ft.Colors.GREEN_700,
            "bgcolor_light": ft.Colors.GREEN_50,
            "bgcolor_dark": ft.Colors.with_opacity(0.2, ft.Colors.GREEN_900),
            "text_color": ft.Colors.GREEN_900 if not is_dark else ft.Colors.GREEN_100,
        },
        "warning": {
            "icon": ft.Icons.WARNING_AMBER_OUTLINED,
            "icon_color": ft.Colors.ORANGE_400 if is_dark else ft.Colors.ORANGE_700,
            "bgcolor_light": ft.Colors.ORANGE_50,
            "bgcolor_dark": ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_900),
            "text_color": ft.Colors.ORANGE_900 if not is_dark else ft.Colors.ORANGE_100,
        },
        "error": {
            "icon": ft.Icons.ERROR_OUTLINED,
            "icon_color": ft.Colors.RED_400 if is_dark else ft.Colors.RED_700,
            "bgcolor_light": ft.Colors.RED_50,
            "bgcolor_dark": ft.Colors.with_opacity(0.2, ft.Colors.RED_900),
            "text_color": ft.Colors.RED_900 if not is_dark else ft.Colors.RED_100,
        },
    }

    theme = config.get(type, config["info"])

    # 🎯 动态选择背景 & 文字色
    bgcolor = theme["bgcolor_dark"] if is_dark else theme["bgcolor_light"]
    text_color = theme["text_color"]

    # 📝 内容文本（确保颜色正确）
    content = ft.Text(
        message,
        size=15,
        weight=ft.FontWeight.W_500,
        color=text_color,
    )

    # ✅ 默认「知道了」按钮（适配主题文字色）
    def close_banner(e):
        banner.open = False
        page.update()

    default_action = ft.TextButton(
        "知道了",
        on_click=close_banner,
        style=ft.ButtonStyle(color=text_color),
    )
    final_actions = actions if actions is not None else [default_action]

    # 🪧 创建 Banner
    banner = ft.Banner(
        content=content,
        leading=ft.Icon(
            leading_icon or theme["icon"],
            color=theme["icon_color"],
            size=28,
        ),
        actions=final_actions,
        bgcolor=bgcolor,
        force_actions_below=force_actions_below,
        content_padding=ft.padding.only(left=20, top=12, right=16, bottom=12),
        leading_padding=ft.padding.only(right=12),
        # divider_color 在深色下建议显式设置（避免默认白色太刺眼）
        divider_color=ft.Colors.with_opacity(0.3, ft.Colors.OUTLINE) if is_dark else ft.Colors.OUTLINE,
    )

    # 📤 显示
    page.open(banner)

    # ⏱️（可选）自动关闭
    if duration_ms:
        def auto_close():
            if banner.open:
                banner.open = False
                page.update()
        page.run_thread(auto_close, delay=duration_ms / 1000)

    return banner
    # 返回实例，便于外部控制（如手动 close）

def get_login_page_contorls() -> list:
    logo = ft.Container(
        content=ft.Text(
            "MewFlow",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PURPLE_500,
            font_family="Maple Mono CN"  # 若字体已加载；否则可省略
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=20),
    )

    # 输入框通用样式
    def create_input_field(label: str, hint: str, password: bool = False,value:str = '') -> ft.TextField:
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            width=320,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
            border_color=ft.Colors.OUTLINE_VARIANT,
            focused_border_color=ft.Colors.PURPLE_400,
            value=value
        )

    server_url_field = create_input_field("服务器地址", "http(s)://...")
    username_field = create_input_field("用户喵", "输入用户喵")
    password_field = create_input_field("密喵", "输入密喵", password=True)

    # 登录按钮
    login_btn = ft.ElevatedButton(
        content=ft.Text("登录", size=18, weight=ft.FontWeight.W_500),
        width=320,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PURPLE_500,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda _: try_auth_navidrome(
            server_url_field.value,
            username_field.value,
            password_field.value,
            None
        )
        # on_click=lambda e: login_save_config(e, server_url_field, username_field, password_field, page),
    )

    # 内置账号按钮（次级风格）
    quick_login_btn = ft.OutlinedButton(
        content=ft.Text("内置账号快速登录", size=16),
        width=320,
        height=48,
        style=ft.ButtonStyle(
            side=ft.BorderSide(2, ft.Colors.PURPLE_300),
            shape=ft.RoundedRectangleBorder(radius=12),
            color=ft.Colors.PURPLE_500,
        ),
        # on_click=lambda e: miaoplay(e, page),
    )

    # 包裹容器：垂直居中布局 + 内边距
    login_container = ft.Container(
        content=ft.Column(
            controls=[
                logo,
                server_url_field,
                username_field,
                password_field,
                login_btn,
                # ft.Container(padding=ft.padding.only(top=12)),  
                # 间距
                quick_login_btn,
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.all(24),
        # width=1000,  
        # 宽屏适配（Flet 会自动限制 max-width）
        alignment=ft.alignment.center,
    )

    # 全局居中（模拟 .App > .login-container）
    page_container = ft.Container(
        content=login_container,
        alignment=ft.alignment.center,
        expand=True,
    )

    return [page_container]


def get_global_middle_center_container(inner_controls:list,give_spacing:int = 0) -> ft.Container:
    """将传入的控件*列表* 放置在一个全局居中的控件里面"""
    return ft.Container(
        content=ft.Column(
            controls=inner_controls,
            alignment=ft.MainAxisAlignment.CENTER,          # 垂直居中内部控件
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 水平居中
            spacing=give_spacing,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
    

main_pages:ft.Page

def main(page:ft.Page):
    global main_pages
    
    main_pages = page
    
    page.adaptive = True
    page.title = 'FletFlow Dev'
    
    def _ez_append_ft_view(route_str:str,contorls:list,):
        '''往page.views中append ft.View(你给定的两个参数)'''
        # '''想省略一点代码'''
        page.views.append(
            ft.View(
            route_str,
            contorls,
            )
        )
        # page.update()
    
    def route_change(route):
        # 传这个参数到底何意味
        print(f"{route =}")
        page.views.clear()
        
        _ez_append_ft_view("/",[get_global_middle_center_container([
            ft.Text("正在初始化数据..",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PURPLE_500,),
            ft.CupertinoActivityIndicator(
            radius=25,
            color=ft.Colors.PURPLE_500,
            animating=True,
            )],give_spacing = 20),
        ]
        )
        
        if page.route == "/setup":
            _ez_append_ft_view(
               "/setup",
               get_login_page_contorls()
            )
        
        
        
        page.update()
        
    
    print(f"{page.route =}")

    page.on_route_change = route_change
    page.go(page.route)
    
    mf_server = page.client_storage.get("mf_access_server")
    mf_user = page.client_storage.get("mf_access_user")
    mf_pwd = page.client_storage.get("mf_access_pwd")
    # mf_last_auth_token = page.client_storage.get("mf_access_last_auth_token")
    
    
    if not mf_server or not mf_user or not mf_pwd:
        print("无配置尝试跳转")
        page.go("/setup")
    else:
        # 这里不知道代码会不会往下跑 所以用else
        try_auth_navidrome(mf_server,mf_user,mf_pwd,None)

        
def try_auth_navidrome(mf_server,mf_user,mf_pwd,mf_last_auth_token):
    """初始化登陆流程"""
    

    
    navApi = NavidromeAPI(
        base_url=mf_server,
        username=mf_user,
        password=mf_pwd,
        last_x_nd_auth_token=mf_last_auth_token
    )
    
    try:
        result = asyncio.run(navApi.auth_and_login())
        # print(f"登陆调用结果: {result}")
        
    except Exception as e:
        show_banner(main_pages,f"登录失败\n{e}",type="error",duration_ms=1500)
        print(f"登录失败: {e}")
        raise
    # loop = asyncio.get_event_loop()
    # future = asyncio.run_coroutine_threadsafe(navApi.auth_and_login(), loop)
    # result = future.result()

    print(f"登陆调用结果{result = }")


    

    # main_pages.client_storage.set("mf_access_server",mf_server)
    # main_pages.client_storage.set("mf_access_user",mf_user)
    # main_pages.client_storage.set("mf_access_pwd",mf_pwd)

# ft.app()
ft.app(main, view=ft.AppView.WEB_BROWSER)