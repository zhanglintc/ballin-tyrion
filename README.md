Xiao霸王学习机
==========

## 简介：
基于 [lxyu/weibo](https://github.com/lxyu/weibo) 项目开发的应用。目的主要是想显示 `“Xiao霸王学习机”` 这个来源。

## 下载：
- [下载最新版](https://zhanglintc.github.io/download/xiaobawang.zip)
- [查看历史版本](https://github.com/zhanglintc/xiaobawang/releases)

## 使用：
打开 `xiaobawang.py` 运行，程序会自动打开浏览器，要求接入你的微博。验证成功以后， 会自动跳转到微博默认回掉地址，url最后会有类似于 `code=xxxxxxxxxx` 的字样，把 `xxxxxxxxxx` 全部拷贝到程序中回车，则会自动生成一个 `token` 文件。这样就可以正常使用了。

## 补充：
程序第一次运行正常应该会显示 `Paste code here:` ，这样才能正常粘贴 code 并运行。
如果没有显示，可以尝试注释掉这两行再运行：

``` python
    reload(sys)
    sys.setdefaultencoding('utf8')
```

目前可以获取自己的timeline，发给自己的评论，可以发微博和带图片的微博。请自行调用函数进行尝试。