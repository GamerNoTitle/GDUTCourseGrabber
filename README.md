## 快速上手

首先，我们先访问教务系统

[广东工业大学教学管理系统](https://jxfw.gdut.edu.cn/)

登录后，我们按下键盘上的`F12`，打开控制台后，选择顶上的网络（Network），在左上角搜索框搜索`login!welcome.action`，然后点击其中的一条记录，选择表头往下滑，找到`Cookie`，右键右边的内容，点击复制值（Copy Value），如果右键没有复制值（部分浏览器没有这个功能）的话，就按下键盘上的`Ctrl`+`C` 复制

![image.png](https://cdn.jsdelivr.net/gh/GamerNoTitle/GDUTCourseGrabber/img/1.png)

接着看图

![image.png](https://cdn.jsdelivr.net/gh/GamerNoTitle/GDUTCourseGrabber/img/2.png)

![image.png](https://cdn.jsdelivr.net/gh/GamerNoTitle/GDUTCourseGrabber/img/3.png)

然后只要等着就可以了

## 高级配置

当你第一次打开本程序后，会自动在程序目录下生成config.json文件

```JSON
{
    "account": {
        "cookie": ""
    },
    "delay": 0.5,
    "courses": [
    ]
}
```


在这里可以调整延迟，就是这里的delay后面的数字啦，越低延迟越少，但是小心被学校封号~


## Reference

https://github.com/FoyonaCZY/GDUT_GrabCourse
