# bae

有2个远程仓库：

1、bae：

//添加远程仓库

git remote add origin https://git.duapp.com/appid4m6z2kda6o

//第一次提交时，把本地的master分支和远程的master分支关联

//-u 表示将远程主机origin设置为缺省主机

git push -u origin master

//正常提交

git push origin master

//如果已经设置origin为缺省主机，可以：

git push

2、github：

git remote add github https://github.com/flywen/bae.git

git push -u github master
