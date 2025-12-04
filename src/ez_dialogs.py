import flet as ft
from typing import List, Optional


def show_banner(
    page: ft.Page,
    message: str,
    *,
    type: str = "info",  # "info" | "success" | "warning" | "error"
    actions: Optional[List[ft.Control]] = None,
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

    return banner
    # 返回实例，便于外部控制（如手动 close）


import flet as ft
from typing import Callable, Optional, List, Tuple


def show_cupertino_alert(
    page: ft.Page,
    title: str = "提示",
    content: str = "请确认此操作。",
    *,
    actions: Optional[List[Tuple[str, Callable, bool]]] = None,
    # actions: [(text, on_click, is_destructive), ...]
    # is_destructive=True 表示危险操作（iOS 红色高亮）
    modal: bool = False,
    barrier_color: Optional[ft.ColorValue] = None,
) -> None:
    """
    显示一个美观、易用的 Cupertino 风格弹窗。

    Args:
        page: 当前页面对象
        title: 弹窗标题（可为空）
        content: 弹窗正文内容
        actions: 按钮列表，每个元素为 (按钮文字, 回调函数, 是否危险操作)
                 默认：[("取消", None, False), ("确定", 默认空回调, False)]
        modal: 是否模态（禁止点击外部关闭）
        barrier_color: 背景遮罩颜色，None 时默认为黑色半透明
    """
    # 默认行为：双按钮（取消/确认）
    if actions is None:
        def _default_confirm(e):
            dlg.open = False
            page.update()

        actions = [
            ("取消", lambda e: setattr(dlg, "open", False) or page.update(), False),
            ("确定", _default_confirm, False),
        ]

    # 构建 CupertinoDialogAction 列表
    cupertino_actions = []
    for text, on_click, is_destructive in actions:
        cupertino_actions.append(
            ft.CupertinoDialogAction(
                text=text,
                on_click=on_click,
                is_destructive_action=is_destructive,
            )
        )

    # 创建对话框
    dlg = ft.CupertinoAlertDialog(
        title=ft.Text(title, weight=ft.FontWeight.BOLD) if title else None,
        content=ft.Text(content),
        actions=cupertino_actions,
        modal=modal,
        barrier_color=barrier_color,
        on_dismiss=lambda e: setattr(dlg, "open", False),  # 安全兜底
    )

    # 打开弹窗
    page.open(dlg)
    page.update()


import flet as ft
from typing import Optional, Callable, Union


def show_snackbar(
    page: ft.Page,
    content: Union[str, ft.Control] = "操作成功",
    *,
    bgcolor: Optional[str] = None,
    color: Optional[str] = None,
    duration: int = 3000,
    action_text: Optional[str] = None,
    on_action: Optional[Callable[[ft.ControlEvent], None]] = None,
    action_color: Optional[str] = None,
    behavior: ft.SnackBarBehavior = ft.SnackBarBehavior.FIXED,
    show_close_icon: bool = False,
    close_icon_color: Optional[str] = None,
    width: Optional[float] = None,
    margin: Optional[ft.PaddingValue] = None,
    padding: ft.PaddingValue = 16,
    elevation: float = 4,
    key: Optional[str] = None,
) -> None:
    # 自动默认背景色
    if bgcolor is None:
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        if isinstance(content, str):
            if content.startswith("✅") or "成功" in content or "完成" in content:
                bgcolor = ft.Colors.GREEN_700 if is_dark else ft.Colors.GREEN_500
            elif content.startswith("⚠️") or "警告" in content:
                bgcolor = ft.Colors.AMBER_800 if is_dark else ft.Colors.AMBER_600
            elif content.startswith("❌") or "错误" in content or "失败" in content:
                bgcolor = ft.Colors.RED_700 if is_dark else ft.Colors.RED_500
            else:
                bgcolor = ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_200
        else:
            bgcolor = ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_200

    # 自动文字颜色对比
    if color is None:
        # 简单判断亮暗度
        if "700" in str(bgcolor) or "800" in str(bgcolor) or "900" in str(bgcolor):
            color = ft.Colors.WHITE
        else:
            color = ft.Colors.BLACK

    # 包装 content
    if isinstance(content, str):
        content = ft.Text(content, color=color, size=14)

    snack = ft.SnackBar(
        content=content,
        bgcolor=bgcolor,
        duration=duration,
        action=action_text,
        on_action=on_action,
        action_color=action_color or (ft.Colors.BLUE_ACCENT_400 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE),
        behavior=behavior,
        show_close_icon=show_close_icon,
        close_icon_color=close_icon_color or color,
        width=width,
        padding=padding,
        elevation=elevation,
    )

    page.open(snack)
    page.update()


def simple_snackbar(page: ft.Page, content: str, duration: int = 3000) -> None:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    bgcolor = ft.Colors.BLACK if is_dark else ft.Colors.WHITE
    color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
    page.open(ft.SnackBar(
        content=ft.Text(content, style=ft.TextStyle(color=color, size=14)),
        duration=duration,
        bgcolor=bgcolor,
        action=None,
    ))
    page.update()
