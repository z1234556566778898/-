# 星坠荒野 / Starfall Wilds

一个单文件离线网页游戏原型：俯视角动作采集 + 基地建造 + 昼夜制（夜晚刷怪）+ 背包放置 + 存档。  
Single-file offline web game prototype: top-down action & gathering + base building + day/night (monsters at night) + inventory placement + save/load.

## 在线试玩 / Play Online

启用 GitHub Pages 后访问：`https://<你的用户名>.github.io/<仓库名>/`  
After enabling GitHub Pages: `https://<username>.github.io/<repo>/`

## 本地运行 / Run Locally

- 直接双击打开 `index.html`（推荐用 Chrome/Edge）  
- Double-click `index.html` (Chrome/Edge recommended)

## 操作 / Controls

- 移动 / Move: WASD 或 方向键 / arrow keys
- 攻击/交互 / Attack/Interact: 鼠标左键 / left click
- 翻滚 / Roll: Shift
- 背包 / Inventory: I
- 制作 / Craft (near workbench): E
- 放置模式 / Placement mode: B
- 选项 / Options: O
- 存档/读档 / Save/Load: F5 / F9

## 内容说明 / Notes

- 昼夜循环：白天安全，夜晚会刷怪并围攻营地。  
- 存档使用浏览器 `localStorage`，同一浏览器同一域名下可持续保存。  
- 3D 主角为单文件内置的 WebGL 程序化渲染（可在选项里关闭）。  

## 工具 / Tools

`tools/blender_generate_astronaut.py`：Blender 脚本，用于生成 Q 版宇航员 GLB（含 Idle/Walk/Run/Attack/Hit/Death 动画）。  

## License

MIT

