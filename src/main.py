import flet as ft
from navidrome import NavidromeAPI
import asyncio
from typing import List, Optional, Callable
from ez_dialogs import show_cupertino_alert, show_snackbar,simple_snackbar
import time


# ===== 【1. 应用状态管理类】=====
class AppState:
    """全局应用状态管理"""
    def __init__(self):
        self.drawer = ft.NavigationDrawer()
        self.current_user = None
        self.is_authenticated = False
        
    def create_drawer(self, page: ft.Page) -> ft.NavigationDrawer:
        """创建导航抽屉"""
        def on_nav_change(e: ft.ControlEvent):
            routes = ["/home", "/library", "/tgt_listen", "/playlist", "/setting"]
            idx = e.control.selected_index
            if idx is not None and 0 <= idx < len(routes):
                page.go(routes[idx])
                page.close(self.drawer)
        
        self.drawer = ft.NavigationDrawer(
            bgcolor=ft.Colors.GREY_900,
            indicator_color=ft.Colors.PURPLE_400,
            indicator_shape=ft.RoundedRectangleBorder(radius=4),
            on_change=on_nav_change,
            controls=[
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="首页",
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.MUSIC_NOTE_OUTLINED,
                    selected_icon=ft.Icons.MUSIC_NOTE,
                    label="音乐库",
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.GROUP_OUTLINED,
                    selected_icon=ft.Icons.GROUP,
                    label="一起听",
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.PLAYLIST_PLAY_OUTLINED,
                    selected_icon=ft.Icons.PLAYLIST_PLAY,
                    label="歌单列表",
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="设置",
                ),
            ],
        )
        return self.drawer

# ===== 【2. 页面工厂函数（解耦抽屉创建）】=====
def get_home_page_controls(page: ft.Page) -> list:
    global recommend_row,latest_albums
    """获取首页控件（不再创建抽屉）"""
    # 使用闭包引用外部的 state.drawer
    # from main import app_state  
    # 假设 app_state 是全局的



    recommend_row = ft.Row(
        [],
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=16,
    )

    latest_albums = ft.Row([],scroll=ft.ScrollMode.ADAPTIVE, spacing=16)
    

    
    home_content = ft.ListView(
        controls=[
            ft.SafeArea(
            ft.Container(
                content=ft.Text("欢迎回来 👋", size=24, weight=ft.FontWeight.BOLD),
                # padding=ft.padding.only(top=20, bottom=8),
            )),
            ft.Text("🎧 随机推荐", size=18, weight=ft.FontWeight.W_600),
            recommend_row,
            ft.Divider(height=24),
            ft.Text("🆕 最新专辑", size=18, weight=ft.FontWeight.W_600),
            latest_albums,
            ft.Container(height=80),
        ],
        padding=0,
        expand=True,
    )

    mini_player = ft.Container(
        content=ft.Row([
            ft.Image(src="./img/def_cover.png", width=40, height=40, fit=ft.ImageFit.COVER, border_radius=8),
            ft.Column([
                ft.Text("未播放", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                ft.Text("点击播放", size=12, color=ft.Colors.GREY_400),
            ], spacing=2, expand=True),
            ft.IconButton(
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PURPLE_600,
                width=44,
                height=44,
                on_click=lambda _: simple_snackbar(page, "播放器开发中"),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        height=60,
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_900),
        padding=ft.padding.symmetric(horizontal=12),
    )

    # AppBar 现在引用外部的抽屉
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.WHITE,
            on_click=lambda _: page.open(app_state.drawer),
        ),
        leading_width=56,
        title=ft.Text("MewFlow", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_900),
        toolbar_height=56,
        adaptive=True,
    )

    
    
    return [
        app_bar,
                  
        ft.Column([
            # ft.Container(height=16),
            home_content, 
            mini_player
        ], expand=True),
    ]


async def init_home_page_ui_datas():
    """加载首页卡片等数据喵~"""
    page = global_router.page

    # 创建骨架卡片
    def create_card(title: str, subtitle: str = "", song_id: str = "") -> ft.Container:
        image_control = ft.Image(
            src="./img/def_cover.png",
            width=120,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=12,
        )
        
        # 小卡片~ meow
        card = ft.Container(
            content=ft.Column([
                image_control,
                ft.Text(title, size=16, weight=ft.FontWeight.W_500, max_lines=1),
                ft.Text(subtitle, size=13, color=ft.Colors.GREY_400, max_lines=1),
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=12,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
            border_radius=16,
            width=140,
            on_click=lambda _: simple_snackbar(page, f"打开 {title} meow~"),
            data={
                "image": image_control,
                "song_id": song_id,
                "title": title
            },
            opacity=0,
        )
        return card

    try:
        # 1. 请求随机歌曲
        data = await navApi.get_random_songs()

        if not data:
            print("获取推荐歌曲失败喵…")
            return

        songs = data.get("randomSongs", {}).get("song", [])
        if isinstance(songs, dict):
            songs = [songs]

        # 清空 UI
        recommend_row.controls.clear()

        cards_info = []
        for song in songs:
            card = create_card(
                song.get("title", "未知歌曲"),
                song.get("artist", "未知艺术家"),
                song.get("id", "")
            )
            recommend_row.controls.append(card)

            cards_info.append({
                "card": card,
                "song_id": song.get("id", "")
            })


        # 3. 先渲染骨架
        page.update()

        # 5. 更新封面 + 透明淡入
        for i in cards_info:
            card = i["card"]
            img = card.data["image"]
            song_id = i["song_id"]
            
            # 默认封面路径

            # 应用封面
            img.src = navApi.build_url("getCoverArt", {"id": song_id, "size": 150})
            img.update()

            # 淡入
            card.opacity = 0
            card.update()
            await asyncio.sleep(0.03)
            card.opacity = 1
            card.update()
        page.update()

    except Exception as e:
        print(f"首页卡片加载异常 meow: {e}")
        import traceback
        print(traceback.format_exc())


    

# ===== 【3. 路由管理器（核心优化）】=====
class Router:
    """路由管理器 - 处理视图栈和页面切换"""
    
    def __init__(self, page: ft.Page, app_state: AppState):
        self.page = page
        self.app_state = app_state
        self.routes = {
            "/": self.loading_view,
            "/setup": self.setup_view,
            "/home": self.home_view,
            
            # 可以继续添加其他路由
        }
        # 加载完view后需要执行的函数
        # 不然加载完控件就定死了
        self.after_router_call = {
            # 路由 , 回调函数 , 是否是异步函数
            "/home": [init_home_page_ui_datas,True],
        }
    
    def loading_view(self) -> ft.View:
        """加载视图"""
        return ft.View(
            "/",
            controls=[get_global_middle_center_container([
                ft.Text("正在初始化数据..", 
                       size=36, 
                       weight=ft.FontWeight.BOLD, 
                       color=ft.Colors.PURPLE_500),
                ft.CupertinoActivityIndicator(
                    radius=25,
                    color=ft.Colors.PURPLE_500,
                    animating=True,
                )
            ], give_spacing=20)],
        )
    
    def setup_view(self) -> ft.View:
        """登录设置视图"""
        return ft.View(
            "/setup",
            controls=get_login_page_contorls(),  # 你的原有函数
        )
    
    def home_view(self) -> ft.View:
        """首页视图"""
        view = ft.View(
            "/home",
            controls=get_home_page_controls(self.page),
        )
        # 将抽屉附加到当前视图
        view.drawer = self.app_state.drawer
        return view
    
    def library_view(self) -> ft.View:
        view = ft.View(
            "/library",
            controls=[],
        )
        return view
    
    def route_change(self, e: ft.RouteChangeEvent):
        """优化的路由变化处理"""
        # 从 RouteChangeEvent 对象中提取路由字符串
        route = e.route
        print(f"路由变化: {route}")
        
        # 清空视图栈，保留第一个视图（如果需要的话）
        if len(self.page.views) == 0:
            # 初始加载，先显示加载页面
            print('初始加载')
            self.page.views.append(self.loading_view())
        
        # 根据路由调用对应的视图工厂
        if route in self.routes.keys():
            # 移除当前视图（如果需要），这里根据你的需求调整
            if len(self.page.views) > 1:
                print("移除当前视图")
                self.page.views.pop()
            
            new_view = self.routes[route]()
            self.page.views.append(new_view)
        else:
            print(f"未知路由: {route}, 跳转到首页")
            # 如果路由不存在，跳转到首页
            if len(self.page.views) > 1:
                print("如果路由不存在 移除当前视图")
                self.page.views.pop()
            new_view = self.routes["/home"]()
            self.page.views.append(new_view)
        
        
        
        print("走到下面")
        
        if route in self.after_router_call.keys():
            print("调用对应路由")
            # 调用路由对应的回调函数
            if self.after_router_call[route][1]:
                # 异步函数
                # asyncio.run(self.after_router_call[route][0]())
                self.page.run_task(self.after_router_call[route][0])
            else:
                self.after_router_call[route][0]()
        
        self.page.update()
        
    
    def view_pop(self, view):
        """处理视图返回（浏览器后退按钮）"""
        self.page.views.pop()
        if self.page.views:
            top_view = self.page.views[-1]
            self.page.go(top_view.route) # type: ignore


# ===== 【4. 主函数重构】=====
app_state = AppState()  # 全局应用状态


def main(page: ft.Page):
    global global_router
    
    page.adaptive = True
    page.title = 'FletFlow Dev'
    
    # 1. 创建应用状态和抽屉
    drawer = app_state.create_drawer(page)
    
    # 2. 初始化路由管理器
    router = Router(page, app_state)
    page.go("/")
    global_router = router
    
    
    # 丢到全局变量
    
    # 3. 设置路由事件处理
    page.on_route_change = router.route_change
    page.on_view_pop = router.view_pop
    
    # 4. 检查凭证并决定初始路由
    mf_server = page.client_storage.get("mf_access_server")
    mf_user = page.client_storage.get("mf_access_user")
    mf_pwd = page.client_storage.get("mf_access_pwd")
    
    if not mf_server or not mf_user or not mf_pwd:
        print("无配置，跳转到设置页面")
        
        # time.sleep(3)
        page.go("/setup")
    else:
        # 尝试自动登录
        print("发现凭证，尝试自动登录...")
        
        page.run_task(
            try_auth_navidrome,
            mf_server=mf_server,
            mf_user=mf_user,
            mf_pwd=mf_pwd,
            mf_last_auth_token=None
        )
        # try_auth_navidrome(mf_server, mf_user, mf_pwd, None)
        # 注意：try_auth_navidrome 内部会调用 page.go("/home")


async def try_auth_navidrome(mf_server,mf_user,mf_pwd,mf_last_auth_token):
    """初始化登陆流程"""
    global navApi
    # from main import global_router
    main_pages:ft.Page = global_router.page
    
    navApi = NavidromeAPI(
        base_url=mf_server,
        username=mf_user,
        password=mf_pwd,
        last_x_nd_auth_token=mf_last_auth_token
    )
    
    try:
        result = await navApi.auth_and_login()
        # print(f"登陆调用结果: {result}")
        print(result)
    except Exception as e:
        print(f"登录失败: {e}")
        show_cupertino_alert(main_pages,
        title="登录失败 请重试",
        content=f"{e}",
    )
        if main_pages.route != "/setup":
            main_pages.go("/setup")
        raise
    # loop = asyncio.get_event_loop()
    # future = asyncio.run_coroutine_threadsafe(navApi.auth_and_login(), loop)
    # result = future.result()

    print(f"登陆调用结果{result = }")
    
    # {'id': 's2m0pwMer6FNvV9mzEfiXs', 'isAdmin': False, 'name': 'dev', 'subsonicSalt': 'f4f0dd', 'subsonicToken': '30acaba3cac6fcdbfd3678776e633ebb', 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG0iOmZhbHNlLCJleHAiOjE3NjUwMTk0MjYsImlhdCI6MTc2NDg0NjYyNiwiaXNzIjoiTkQiLCJzdWIiOiJkZXYiLCJ1aWQiOiJzMm0wcHdNZXI2Rk52VjltekVmaVhzIn0.UTk50kjiRLXpnyqr8QgolMh22rbnHMb-mCnsM5UiJNA', 'username': 'dev'}
    mx1 ="管理员" if result['isAdmin'] == True else "用户"
    
    simple_snackbar(main_pages,f'尊敬的{mx1}{result["name"]} 欢迎回来',duration=2000)
    await main_pages.client_storage.set_async("mf_access_server",mf_server)
    await main_pages.client_storage.set_async("mf_access_user",mf_user)
    await main_pages.client_storage.set_async("mf_access_pwd",mf_pwd)
    main_pages.go("/home")


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

    server_url_field = create_input_field("服务器地址", "http(s)://...",value="http://192.168.16.109:42280")
    username_field = create_input_field("用户喵", "输入用户喵",value='dev')
    password_field = create_input_field("密喵", "输入密喵", password=True,value='123')

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
        on_click=lambda _: 
            global_router.page.run_task(
            try_auth_navidrome,
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

# ft.app(main)
ft.app(main, view=ft.AppView.WEB_BROWSER)