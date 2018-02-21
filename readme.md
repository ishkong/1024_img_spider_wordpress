# 1024_img_spider_wordpress注意事项：
`仅支持python3`

演示站:https://fulishe.in/1024

# python所需库：
```bash
pip3 install requests
pip3 install pymysql
```

# 关于使用
需要打开脚本文件设置连接的mysql信息，在代码第11行</br>
还有要修改第26,28行的图床key，和图床url，只支持chevereto</br>
第80行文章分类ID（默认未分类）</br>
保留了采集一次后停止60s后再采集，如果不需要，删除第121行即可</br>

# 使用方法：
```bash
chmod +x spider.py
python3 spider.py
```

# 关于程序
综合自
https://github.com/eqblog/1024_img_spider_threads
和
https://raw.githubusercontent.com/eqblog/mm131_spider_wordpress
