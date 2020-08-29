# 新闻资讯网站

技术: Python3+Flask+Mysql+Redis

生成管理员： python manager.py create_superuser -u 账号 -p 密码

生成数据库： use database; source ***.sql

## 本地部署

运行： python manager.py create_superuser -u 账号 -p 密码

python manager.py run server

## Docker部署

docker build -t ImageName:TagName .

docker run -d ImageName:TagName
