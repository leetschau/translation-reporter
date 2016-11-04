# Translation Reporter

记录翻译数据，计算翻译速度，汇总翻译进度。

## 数据文件格式说明

原始数据文件：`trep.dat`.

每一行时间记录格式为：
`time-string action-name page-position`.

其中`time-string`是ISO 8601格式的字符串，
使用`datetime.datetime.now().isoformat()`生成（Python实现）。

`action`是`rec/list/report`3者之一，分别代表记录事件、
打印分析结果（文本）和显示分析报告（图片）；

`page-position`表示事件发生时页面的位置，可以是印刷页码（用print表示），
也可以是PDF文件页面序号（用pdf表示），保持统一即可，用精确到小数点后1位的数字表示。

例如`14.9`表示第14页接近结尾部分，`231.3`表示第231页前三分之一位置，
`23.0`表示第23页第1行，`45.5`表示第45页正中间等。

示例：
```
Title: Functional Python Programming
Total Pages: 351
Page Type: print

Action Records:
------
2016-11-03T10:06:49.656754 start 12.7
2016-11-03T11:06:49.656754 end 14.2
------
2016-11-04T10:06:49.656754 start 14.2
2016-11-04T11:06:49.656754 pause
2016-11-04T12:06:49.656754 resume
2016-11-04T13:06:49.656754 end 17.2
------
```

## Installation

```
git clone https://github.com/leetschau/translation-reporter.git ~/apps/translation-reporter
sudo ln -s ~/apps/translation-reporter/trep.py /usr/local/bin/trep
```

## Usage

```
cd /path/to/your/project
cp ~/apps/translation-reporter/trep-sample.dat trep.dat
```

修改`trep.dat`中的书名、总页数、页码类型后，就可以使用了：

命令列表见`trep -h`.
