import flet as ft
import flet_audio as fa 
from navidrome import NavidromeAPI
import asyncio
from typing import List, Optional, Callable,Any
import time

from ez_dialogs import show_cupertino_alert, show_snackbar,simple_snackbar

class AuidoManager:
    def __init__(self, page:ft.Page):
        self.page = page
        
        self.playmode_ray_dict = {
            0: "顺序播放",
            1: "单曲循环",
            2: "随机播放",
            3: "列表循环",
        }
        self.current_play_mode = 0
        self.playlist = [
            # [id,title,artist]
            
        ]
        self.current_play_index = -1
        
        
        self.current_play_title = ""
        self.current_play_artist = ""
        self.current_play_cover_src = ""
        # self._re_build_auido_elw()
        
        self.auido_playing_state = 0
    
    # def add_src_to_auido_player(self,src:str,need_tras_to_b64:bool=False):
    def _audio_when_play_complete(self):
        """音频播放完成回调"""
        # if self.current_play_mode == 1:
        
        # print(f"{self.auido_player_elw.get_duration() =}")
        # print(f"{self.auido_player_elw.get_current_position() =}")
        # print("play complete")
        raise NotImplementedError()
    
    def change_play_mode(self):
        """切换播放模式"""
        self.current_play_mode = (self.current_play_mode + 1) % 4
        raise NotImplementedError()
    
    def load_last_played_playlist(self,page:ft.Page):
        """加载上一次播放的播放列表"""
        raise NotImplementedError()
    def load_last_playmode(self):
        """加载上一次的播放模式"""
        raise NotImplementedError()
    
    def del_song_from_playlist(self,index:int,song_id:str|None = None):
        """从播放列表中删除指定索引或者指定的歌曲ID的歌曲"""
        raise NotImplementedError()

    def add_song_to_next_play(self,song_id:str):
        """添加歌曲到播放列表的下一首"""
        raise NotImplementedError()
    
    def pause_or_resume(self,e):
        """暂停或恢复播放"""
        if self.auido_playing_state == 0:
            self.auido_player_elw.resume()
        elif self.auido_playing_state == 1:
            self.auido_player_elw.pause()
    
    def _on_auido_staus_change_fire(self,e):
        """播放状态改变"""
        if e.state == ft.AudioState.PAUSED:
            self.auido_playing_state = 0

        elif e.state == ft.AudioState.PLAYING:
            self.auido_playing_state = 1
    
    def play_give_music_id(self,music_id:str):
        """播放给定的音乐的音乐ID"""
        self.page.run_task(self._auido_play_helper,music_id)
    
    async def _auido_play_helper(self,music_id:str):
        print("ready to play",music_id)
        music_url_src = await navApi.stream_url(music_id)
        print(f"{music_url_src = }")
        self._re_build_auido_elw(music_url_src)
        await self.update_mini_player(music_id)
        
    async def update_mini_player(self,music_id:str):
        song_infos = await navApi.get_song(music_id)
        print(f"{song_infos = }")
        if not song_infos:
            print("no songs info?")
            return
        title = song_infos['song']['title'] # type: ignore
        # album = song_infos['song']['album'] # type: ignore
        artist = song_infos['song']['artist'] # type: ignore
        
        art_src = navApi.build_url('getCoverArt', {'id': music_id, 'width': 200})
        
        # mini_player.content.content.controls[0].src = art_src # type: ignore
        # # 修改歌名
        # mini_player.content.content.controls[1].controls[0].value = title # type: ignore
        # # 修改艺术家
        # mini_player.content.content.controls[1].controls[1].value = artist # type: ignore

        self.current_play_title = title
        self.current_play_artist = artist
        self.current_play_cover_src = art_src

        self.page.update()
        
        
    def _re_build_auido_elw(self,src:str|None,srcb64:str|None = None,auto_play:bool = True):
        
        self.auido_player_elw = fa.Audio(
            src=src if src else None,
            src_base64=srcb64 if srcb64 else None,
            autoplay=auto_play,
            volume=1,
            on_seek_complete=lambda _: self._audio_when_play_complete(),
            on_loaded=lambda _: print("audio loaded"),
            on_state_changed=self._on_auido_staus_change_fire,
        )
        self.page.overlay.clear()
        self.page.overlay.append(self.auido_player_elw)
        print(f"{self.page.overlay = }")
        self.page.update()
        
        

    def _get_shit_from_client(self,key:str) -> Any | None:
        """从客户端获取缓存的数据"""
        return self.page.client_storage.get(key)
    




# ===== 【1. 应用状态管理类】=====
class AppState:
    """全局应用状态管理"""
    def __init__(self):
        global _last_swipe_time, _DEBOUNCE_INTERVAL
        
        self.drawer = ft.NavigationDrawer()

        # self.current_user = None
        # self.is_authenticated = False

    
    def create_drawer(self, page: ft.Page,selected_index:int = 0) -> ft.NavigationDrawer:
        """创建导航抽屉"""
    
        
        def on_nav_change(e: ft.ControlEvent):
            routes = ["/home", "/library", "/tgt_listen", "/playlist", "/setting"]
            idx = e.control.selected_index
            if idx is not None and 0 <= idx < len(routes):
                page.go(routes[idx])
                # page.close(self.drawer)
        
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
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.MUSIC_NOTE_OUTLINED,
                    selected_icon=ft.Icons.MUSIC_NOTE,
                    label="音乐库",
                ),
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.GROUP_OUTLINED,
                    selected_icon=ft.Icons.GROUP,
                    label="一起听",
                ),
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.PLAYLIST_PLAY_OUTLINED,
                    selected_icon=ft.Icons.PLAYLIST_PLAY,
                    label="歌单列表",
                ),
                ft.Container(height=12),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="设置",
                ),
            ],
            selected_index=selected_index,
        )
        return self.drawer

    def build_mini_player(self, page: ft.Page) -> ft.Container:
        global _last_swipe_time, _DEBOUNCE_INTERVAL
        def show_feedback(direction: str):
            """direction: 'prev' 或 'next'"""
            # 缩放封面
            cover = mini_player.content.content.controls[0]  # type: ignore
            # Image
            row = mini_player.content.content  # type: ignore
            # Row inside GestureDetector

            # 创建方向提示图标（临时）
            icon = ft.Icon(
                ft.Icons.SKIP_PREVIOUS_ROUNDED if direction == "prev" else ft.Icons.SKIP_NEXT_ROUNDED,
                size=24,
                color=ft.Colors.WHITE,
            )
            overlay = ft.Container(
                content=icon,
                width=40,
                height=40,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.PURPLE_700),
                border_radius=20,
                alignment=ft.alignment.center,
            )

            # 插入 overlay 到 Row 末尾（不破坏结构）
            row.controls.append(overlay)
            mini_player.bgcolor = ft.Colors.with_opacity(0.95, ft.Colors.GREY_800)  # 背景变亮
            cover.scale = 1.1  # 封面放大

            mini_player.update()

            # 300ms 后恢复
            def _reset(_):
                if overlay in row.controls:
                    row.controls.remove(overlay)
                cover.scale = 1.0
                mini_player.bgcolor = ft.Colors.with_opacity(0.9, ft.Colors.GREY_900)
                mini_player.update()

            # 使用 page.run_after 微延迟恢复（避免阻塞）
            # asyncio.sleep(0.3)
            time.sleep(0.3)
            _reset("")

        _last_swipe_time = 0  # 上次触发时间戳（秒级 float）
        _DEBOUNCE_INTERVAL = 0.05  # 50ms 防抖阈值

        def is_swipe_debounced() -> bool:
            global _last_swipe_time
            now = time.time()
            if now - _last_swipe_time < _DEBOUNCE_INTERVAL:
                return True  # 还在冷却中
            _last_swipe_time = now
            return False

        def on_pan_update(e: ft.DragUpdateEvent):
            # e.delta_x 是本次拖动的水平增量（正：右滑；负：左滑）
            # 为避免误触，可加阈值（比如 |Δx| > 50 才判定为有效滑动）
            if is_swipe_debounced():
                return  # 防抖拦截
            threshold = 50
            if abs(e.delta_x) > threshold:
                if e.delta_x > 0:
                    # 从左往右滑 → 上一首
                    show_feedback("prev")
                    print("prev song")
                    # prev_song()
                    # ← 你填函数名
                else:
                    show_feedback("next")
                    print("next song")
                    # 从右往左滑 → 下一首
                    # next_song()
                    # ← 你填函数名
                # 防止多次触发：可通过 e.control.data 标记或禁用短时检测（此处简化）
                # 建议后续加防抖：如记录 last_swipe_time 并限制 500ms 内只触发一次

        
        mini_player = ft.Container(
            content=ft.GestureDetector(
                content=ft.Row([
                    ft.Image(
                        src="./img/def_cover.png",
                        width=40,
                        height=40,
                        fit=ft.ImageFit.COVER,
                        border_radius=8,
                        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),  # 平滑缩放
                    ),
                    ft.Column([
                        ft.Text("未播放", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.Text("点击播放", size=12, color=ft.Colors.GREY_400),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.PURPLE_600,
                        width=44,
                        height=44,
                        # on_click=lambda _: simple_snackbar(page, "播放器开发中"),
                        
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                on_pan_update=on_pan_update,
                drag_interval=10,
            ),
            height=60,
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_900),
            padding=ft.padding.symmetric(horizontal=12),
            border_radius=8,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),  # 背景色平滑过渡
        )

        return mini_player

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
            on_click=lambda _: auidoManager.play_give_music_id(song_id),
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

        songs = data.get("randomSongs", {}).get("song", [])  # type: ignore
        if isinstance(songs, dict):
            songs = [songs]

        # 清空 UI
        home_ui_recommend_row.controls.clear()

        cards_info = []
        for song in songs:
            card = create_card(
                song.get("title", "未知歌曲"),
                song.get("artist", "未知艺术家"),
                song.get("id", "")
            )
            home_ui_recommend_row.controls.append(card)

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
        # global app_bar
        
        self.page = page
        self.app_state = app_state
        
        self.routes = {
            "/": self.loading_view,
            "/setup": self.setup_view,
            "/home": self.home_view,
            "/library": self.library_view,
            
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
            controls=get_setup_page_contorls(),  # 你的原有函数
        )
    
    def home_view(self) -> ft.View:
        """首页视图"""
        # 我真没招了 每次都要新建一次
        self.app_state.create_drawer(self.page)
        # 不然就报 AssertionError:
        # NavigationDrawer Control must be added to the page first
        # 给我修力竭了
        
        view = ft.View(
            "/home",
            controls=get_home_page_controls(self.page),
            drawer=self.app_state.drawer,
        )

        # view.drawer = self.app_state.drawer
        self.page.drawer = self.app_state.drawer
        # 你妈的呀 为什么是给page赋值才可以啊
        return view
    
    
    def library_view(self) -> ft.View:
        self.app_state.create_drawer(self.page,1)
        
        view = ft.View(
            "/library",
            controls=get_library_page_controls(self.page),
            drawer=self.app_state.drawer,
        )

        # view.drawer = self.app_state.drawer
        self.page.drawer = self.app_state.drawer
        
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

            # # 路由问题: 此处 self.page.views 因为append了新的view
            # # 抽屉就爆炸了
            # # new_view.drawer = self.app_state.drawer
            # self.page.views[0].drawer = self.app_state.drawer
            # self.page.views[-1].drawer = self.app_state.drawer
            
            # print(f'{self.page.views[-1] = }')
            # print(f"{self.page.views =}")

        else:
            print(f"未知路由: {route}, 跳转到首页")
            # 如果路由不存在，跳转到首页
            if len(self.page.views) > 1:
                print("如果路由不存在 移除当前视图")
                self.page.views.pop()
            new_view = self.routes["/home"]()
            self.page.views.append(new_view)
            
            
            # self.page.views[-1].drawer = self.app_state.drawer
            # ? 我刚删就tm出问题 ?

        self.page.drawer = self.app_state.drawer
        
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
    global global_router,auidoManager
    
    page.adaptive = True
    page.title = 'FletFlow Dev'
    
    # 1. 创建应用状态和抽屉
    
    
    
    auidoManager = AuidoManager(page)
    
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

    print(f"登陆调用结果{result = }")
    
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
def get_setup_page_contorls() -> list:
    
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

def get_home_page_controls(page: ft.Page) -> list:
    global home_ui_recommend_row,home_ui_latest_albums
    """获取首页控件（不再创建抽屉）"""
    # 使用闭包引用外部的 state.drawer
    # from main import app_state  
    # 假设 app_state 是全局的

    home_ui_recommend_row = ft.Row(
        [],
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=16,
    )

    home_ui_latest_albums = ft.Row([],scroll=ft.ScrollMode.ADAPTIVE, spacing=16)
    
    home_content = ft.ListView(
        controls=[
            ft.SafeArea(
            ft.Container(
                content=ft.Text("欢迎回来 👋", size=24, weight=ft.FontWeight.BOLD),
                # padding=ft.padding.only(top=20, bottom=8),
            )),
            ft.Text("🎧 随机推荐", size=18, weight=ft.FontWeight.W_600),
            home_ui_recommend_row,
            ft.Divider(height=24),
            ft.Text("🆕 最新专辑", size=18, weight=ft.FontWeight.W_600),
            home_ui_latest_albums,
            ft.Container(height=80),
        ],
        padding=0,
        expand=True,
    )





    # AppBar 现在引用外部的抽屉

    app_bar_ = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=ft.Colors.WHITE,
                on_click=lambda _: page.open(app_state.drawer),
                # on_click=lambda _: None,
            ),
            leading_width=56,
            title=ft.Text("MewFlow", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_900),
            toolbar_height=56,
            adaptive=True,
        )


    return [
        app_bar_,     
        ft.Column([
            # ft.Container(height=16),
            home_content, 
            app_state.build_mini_player(page)
        ], expand=True),
    ]

def get_library_page_controls(page: ft.Page) -> list:
    """
    返回「资料库」页面控件列表，参照 HTML 原型 + 美观暗色风格
    """
    # === 搜索与排序区域 ===
    search_input = ft.TextField(
        hint_text="搜索音乐",
        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
        border_radius=24,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
        width=280,
        text_size=14,
        bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ft.Colors.PURPLE_500,
        on_submit=lambda e: search_some_thing(),  # 绑定回车搜索
    )

    search_btn = ft.IconButton(
        icon=ft.Icons.SEARCH_ROUNDED,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PURPLE_600,
        width=44,
        height=44,
        on_click=lambda _: search_some_thing(),
    )

    sort_order = ft.Dropdown(
        value="createdAt",
        options=[
            ft.dropdown.Option("createdAt", "按创建时间"),
            ft.dropdown.Option("random", "随机"),
            ft.dropdown.Option("duration", "按时长"),
            ft.dropdown.Option("playCount", "按播放次数"),
            ft.dropdown.Option("title", "按标题"),
        ],
        width=160,
        border_radius=8,
        content_padding=8,
        text_size=13,
        bgcolor=ft.Colors.GREY_800,
        on_change=lambda e: apply_sort(),
    )

    sort_func = ft.Dropdown(
        value="DESC",
        options=[
            ft.dropdown.Option("DESC", "倒序"),
            ft.dropdown.Option("ASC", "正序"),
        ],
        width=100,
        border_radius=8,
        content_padding=8,
        text_size=13,
        bgcolor=ft.Colors.GREY_800,
        on_change=lambda e: apply_sort(),
    )

    play_all_btn = ft.ElevatedButton(
        "播放部分",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PURPLE_700,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=lambda _: play_library_all(),
    )

    inf_play_btn = ft.ElevatedButton(
        "无限播放",
        icon=ft.Icons.REPEAT_ROUNDED,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREY_700,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=lambda _: toggle_inf_play_mode(),
    )

    # 搜索区：输入框 + 按钮（小屏换行）
    search_section = ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=ft.Row([search_input, search_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                col={"xs": 12, "sm": 8, "md": 6},
                padding=ft.padding.only(bottom=8),
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # 排序与按钮区
    sort_section = ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=ft.Row([sort_order, sort_func], spacing=8),
                col={"xs": 12, "sm": 7},
            ),
            ft.Container(
                content=ft.Row([play_all_btn, inf_play_btn], spacing=8),
                col={"xs": 12, "sm": 5},
                alignment=ft.alignment.center_right,
            ),
        ],
        spacing=12,
    )

    # === 音乐列表容器 ===
    music_list_view = ft.ListView(
        expand=True,
        spacing=8,
        padding=ft.padding.only(top=16),
    )

    # 模拟 5 个示例项（实际应由数据填充）
    def create_music_item(index: int, title: str, artist: str, duration: str, cover_src: str = "./img/def_cover.png"):
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Stack(
                    controls=[
                        ft.Image(
                            src=cover_src,
                            width=48,
                            height=48,
                            fit=ft.ImageFit.COVER,
                            border_radius=6,
                            error_content=ft.Container(
                                bgcolor=ft.Colors.GREY_700,
                                width=48,
                                height=48,
                                border_radius=6,
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.MUSIC_NOTE, size=20, color=ft.Colors.GREY_400),
                            ),
                        ),
                        ft.Container(
                            content=ft.Text(f"#{index+1}", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            width=20,
                            height=20,
                            bgcolor=ft.Colors.PURPLE_600,
                            border_radius=10,
                            alignment=ft.alignment.bottom_right,
                            right=0,
                            bottom=0,
                        ),
                    ],
                ),
                title=ft.Text(title, size=15, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                subtitle=ft.Text(artist, size=12, color=ft.Colors.GREY_400),
                trailing=ft.Text(duration, size=13, color=ft.Colors.GREY_300, width=40, text_align=ft.TextAlign.RIGHT),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda _: simple_snackbar(page, f"播放 {title}"),
            ),
            bgcolor=ft.Colors.GREY_800,
            border_radius=8,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            # hover 效果增强（可选）
            # on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.GREY_700 if e.data == "true" else ft.Colors.GREY_850) or e.control.update(),
        )

    # 填充示例数据（后续替换为真实数据）
    for i, (title, artist, dur) in enumerate([
        ("夜の蝶", "DECO*27", "3:42"),
        ("アイドル", "YOASOBI", "3:27"),
        ("群青", "YOASOBI", "4:01"),
        ("Pretender", "Official髭男dism", "4:18"),
        ("SPECIALZ", "King Gnu", "3:50"),
    ]):
        music_list_view.controls.append(create_music_item(i, title, artist, dur))

    # === 页面主体布局 ===
    library_content = ft.Column(
        controls=[
            ft.Container(height=12),
            search_section,
            sort_section,
            ft.Divider(height=24, color=ft.Colors.TRANSPARENT),
            ft.Text("🎧 我的资料库", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            ft.Container(height=8),
            ft.Container(
                content=music_list_view,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ],
        expand=True,
    )

    # === AppBar（与首页一致）===
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.WHITE,
            on_click=lambda _: page.open(app_state.drawer),
            # on_click=lambda _: None,
        ),
        leading_width=56,
        title=ft.Text("资料库", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_900),
        toolbar_height=56,
        adaptive=True,
    )

    return [
        app_bar,
        ft.Column([
            library_content,
            # 底部 mini_player（复用首页的）
            app_state.build_mini_player(page),
        ], expand=True),
    ]
    
# === 占位回调函数（后续替换为真实逻辑）===
def search_some_thing():
    print("[Library] 触发搜索")

def apply_sort():
    print("[Library] 应用排序")

def play_library_all():
    print("[Library] 播放部分")

def toggle_inf_play_mode():
    print("[Library] 切换无限播放模式")

# ft.app(main)
ft.app(main, view=ft.AppView.WEB_BROWSER)