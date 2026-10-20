# 验证记录

日期：2026-10-20。范围：用户选定的 Skill＋执行脚本，不启用宿主扩展。

## 已完成

- `node --test tools/skills/shared/wl-web-auto/scripts/lifecycle*.test.mjs`：17/17通过；独立验证者复跑同样通过。
- `node tools/skills/shared/wl-web-auto/scripts/self-test.mjs`：原有证据目录/截图模式/并发上限5/5通过。
- `node --check tools/skills/shared/wl-web-auto/scripts/lifecycle.mjs`：通过。
- 真实原生Bridge本地HTTP夹具：A/B随机session返回不同page，finish A后B仍可读标题；之后finish B，两者session列表均空。临时HTTP服务已停，无业务写入；未关共享daemon或历史会话。具体task id见Skill参考说明。
- 真实整任务runner：Node子进程退出7，finally执行租约释放，runner返回7。未创建业务页面。
- `uv run --offline --no-project --python 3.12.9 --with pyyaml python install.py --catalog-only`：85个登记目录刷新成功，未联网同步或安装Skill。最初不带已缓存PyYAML的运行因缺yaml模块失败；使用uv离线缓存后成功，未修改项目依赖。
- 本次路径 `git diff --check`：通过。仓库既有未提交变更保留，没有提交/推送。

## 独立核对

通过Herdr启动Pi并显式`--thinking high`，验证者确认会话high。只读本次变更与直接原生契约，不操作浏览器；初轮发现绑定未确认仍放行业务动作，已修复并增加回归。最终：范围内无剩余已发现阻断，17/17通过。完整报告在本机 `/tmp/opencli-lifecycle-review-final.md`（临时证据，非长期保证）。

## 未覆盖与剩余限制

- released/releaseConfirmed只表示租约释放应答及session空列表；物理关页、清空、调试横幅没有独立运行证明。原生扩展可能吞关页异常。pageCleanup明确not-independently-verified。
- 最后空白容器与共享daemon保留。本次未实现全部标识消失或服务自动退出，不能把用户原始痛点写成完全解决。
- 用户级Pi扩展未启用；交互Agent必须显式finish。直接绕过Skill使用opencli仍不会被强制接管。
- 借用用户真实页面、真实OS信号/完整进程树、SIGKILL/断电、空闲超时未测试；hold不取消原生超时。
- 固定支持OpenCLI 1.8.8 / 扩展1.0.24；版本变化停止受管执行，先重验原生契约。
- 需求HTML为Markdown生成的阅读副本，静态生成成功；本轮未执行文档视觉/截图验收，不计视觉通过。

## 结果

在本轮确认的“仅更新Skill和执行脚本”范围内交付完成。下一次加载当前Skill即可使用统一入口；现有软链接指向唯一正文，不需要全局安装。自动收尾范围只限整任务runner可执行finally的情形；不能承诺所有宿主、所有异常和任意直接调用都受管。
