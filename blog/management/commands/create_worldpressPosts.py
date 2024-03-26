#coding=utf-8
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

import MySQLdb
from blog.models import Article, Tag, Category

# WordPress6.4.1 版本 数据库库格式，其他版本没有测试过
def Mysqlsss():

    conn = MySQLdb.connect(
        host='1.2.3.4',# 数据库地址
        port=3306,
        user='数据库用户名',
        passwd='sdfsdfdfbb', # 密码
        db='数据库名',
    )
    try:
        with conn.cursor() as cur:
            sql = '''SHOW TABLES'''
            cur.execute(sql)
            tableName_posts = None  # 文章数据
            wordp_term_taxonomy = None  # id 表示这个是分组还是标签 还有又多少文章使用当这个标签或者分组 分组的父分组
            wordp_term_relationships = None  # 文章id对应的分组和标签
            wordp_term = None  # 标签和分组
            for i in cur.fetchall():
                if (i[0][-6:] == "_posts"):
                    tableName_posts = i[0]
                elif (i[0][-14:] == "_term_taxonomy"):
                    wordp_term_taxonomy = i[0]
                elif (i[0][-19:] == "_term_relationships"):
                    wordp_term_relationships = i[0]
                elif (i[0][-6:] == "_terms"):
                    wordp_term = i[0]

            cur.execute("select * from {0}".format(tableName_posts))
            posts = cur.fetchall()

            cur.execute("select * from {0}".format(wordp_term_taxonomy))
            term_taxonomy = cur.fetchall()

            cur.execute("select * from {0}".format(wordp_term_relationships))
            term_relationships = cur.fetchall()

            cur.execute("select * from {0}".format(wordp_term))
            term = cur.fetchall()

            return posts, term_taxonomy, term_relationships, term


    except Exception as f:
        # 这里是执行异常的
        print(f)
    finally:
        conn.close()

class Command(BaseCommand):
    help = 'create test datas'

    def handle(self, *args, **options):
        # print(123,make_password('test!q@w#eTYU'))
        # user = get_user_model().objects.get_or_create(username='测试用户2')
        user = get_user_model().objects.all()[0]
        #print(user)
        # password=make_password('test!q@w#eTYU')
        posts, term_taxonomy, term_relationships, term = Mysqlsss()

        # 添加分类和标签
        for i in term_taxonomy:

            if(i[2]=="post_tag"):
                # pass

                # tag = Tag()
                # tag.name = "标签" + str(i[1])
                for term_item in term:
                    if(term_item[0] == i[1]):
                        Tag.objects.get_or_create(name=term_item[1])
                        break
                # print(i[1])
            elif(i[2]=="category"):
                # 用一个列表存它们的依赖关系依次是父节点，子节点，子子节点，最后一个应该是没有父节点，
                node_list = list()
                # 这里会导致 子节点会在包含一边父节点
                while(i[4] != 0):

                    temp_taxonomy = [0,0,0,0]
                    for taxonomy in term_taxonomy:
                        if(taxonomy[0] == i[4]):
                            temp_taxonomy = taxonomy
                            break

                    for tagcar in term:
                        if tagcar[0] == i[1]:
                            name = tagcar[1]
                            if not(name in node_list):
                                node_list.append(name)
                        elif tagcar[0] == temp_taxonomy[1]:
                            name = tagcar[1]
                            if not(name in node_list):
                                node_list.append(name)

                        # 这里如果标签多了 建议都找到了，就跳出遍历


                    i = temp_taxonomy

                if not node_list:
                    for tagcar in term:
                        if tagcar[0] == i[1]:
                            name = tagcar[1]
                            if not(name in node_list):
                                node_list.append(name)
                            break

                if  node_list:
                    if len(node_list)==1:
                        Category.objects.get_or_create(name=node_list[0], parent_category=None)
                    else:

                        Categoryid = None
                        for node in node_list:
                            Categoryid = Category.objects.get_or_create(name=node, parent_category=Categoryid)[0]


        for post_ in posts:
            # 如果遇到文章历史,草稿，未发布，直接跳出
            if post_[17] != 0 or post_[20] !="post" or post_[7] != "publish":
                continue

            postid = post_[0]
            catandtars = [] # 这个文章对应 标签和分类id
            catandtarid = [] # 首id是分类id，后面全是标签id
            for term_relationship in term_relationships:
                if(term_relationship[0] == postid):
                    catandtars.append(term_relationship[1])

            if not catandtars:
                # 文章没有找到对应的分类id 跳出
                continue
            for catandtar in catandtars:
                for term_taxonomyItem in term_taxonomy:
                    if catandtar == term_taxonomyItem[0]:
                        # print("没有相等的？")
                        if term_taxonomyItem[2] == "category":
                            #分组的id term[1]
                            if not catandtarid:
                                catandtarid.append(term_taxonomyItem[1])
                            else:
                                # catandtarid.
                                catandtarid.insert(0,term_taxonomyItem[1])

                        elif term_taxonomyItem[2] == "post_tag":
                            # 标签的id term[1]
                            catandtarid.append(term_taxonomyItem[1])

            # 没有找到对应文章对应的分类id 跳出
            if not catandtarid:
                continue
            categoryid = None
            tarids = list()
            for index,catandtarid_item in zip(range(len(catandtarid)),catandtarid):
                for term_item in term:
                    if term_item[0] == catandtarid_item:
                        if index == 0:
                            # 这里是分组
                            QuerySet = Category.objects.filter(name=str(term_item[1]))
                            if len(QuerySet) > 0:
                                categoryid = QuerySet[0]

                        else:
                            # 这里是标签
                            QuerySet = Tag.objects.filter(name=str(term_item[1]))
                            if len(QuerySet) > 0:
                                tarids.append(QuerySet[0].id)
                        break

            if categoryid:
                # print(categoryid,tarids,post_[5])
                try:
                    article = Article.objects.get_or_create(
                        category=categoryid,
                        title=post_[5],
                        body=post_[4],
                        author=user,
                        type='a', # a 是文章
                        comment_status='o', # o 允许评论
                        pub_time=post_[2],
                        status='p' # p 已发表

                    )[0]
                except Exception as e:
                    print(e)
                    print(post_[5])
                # 添加标签还有问题，需要作者解决一下
                # for i in tarids:
                #     tag = Tag()
                #     tag.name = "标签" + str(i)
                #     tag.save()
                #     article.tags.add(tag)
                #     article.tags.add(basetag)
                article.save()
            else:
                print("没有",post_[5])














        #
        # category.save()

        # basetag.name = "标签"
        # basetag.save()


        #
        # from djangoblog.utils import cache
        # cache.clear()
        # self.stdout.write(self.style.SUCCESS('created test datas \n'))
