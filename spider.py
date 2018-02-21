import threading
import mimetypes,json
import requests
import re,os,time,pymysql

class wordpress_post:
    def __init__(self,tittle,content):
        self.tittle=tittle
        self.content=content
    def mysql_con(self):
        conn = pymysql.connect(host='', port=3306, user='', passwd='', db='', charset='utf8') #数据库填这里
        return conn
    def up(self):
        times=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql="INSERT INTO wp_posts(post_author,post_date,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_name,to_ping,pinged,post_modified,post_content_filtered,post_parent,menu_order,post_type,comment_count) VALUES ('1','%s','%s','%s','','publish','open','open','%s','','','%s','','0','0','post','0')" % (str(times),str(self.content),str(self.tittle),str(self.tittle),str(times))
        return sql
    def cat(self,ids,cat):
        sql="INSERT INTO wp_term_relationships(object_id,term_taxonomy_id,term_order) VALUES (%s,%s,'0')"%(ids,cat)
        return sql
    def close_mysql(self,cursor,conn):
        conn.commit()
        cursor.close()
        conn.close()

def upload(files):
    APIKey = "" #API填这里
    format = "json"
    url = "http://你的域名/api/1/upload/?key="+ APIKey + "&format=" + format #图床地址
    r = requests.post(url, files = files)
    return json.loads(r.text)
    
def formatSource(filename):
    imageList = []
    type = mimetypes.guess_type(filename)[0]
    imageList.append(('source' , (filename , open(filename , 'rb') , type)))
    return imageList
        
class myThread (threading.Thread):
    def __init__(self, url, dir, filename):
        threading.Thread.__init__(self)
        self.threadID = filename
        self.url = url
        self.dir = dir
        self.filename=filename
    def run(self):
        download_pic(self.url,self.dir,self.filename)
    
def download_pic(url,dir,filename):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'https://t66y.com'}
    req=requests.get(url=url,headers=headers)
    if req.status_code==200:
        with open('temp/'+str(filename)+'.jpg','wb') as f:
            f.write(req.content)

def upload_img(page,tittle):
    for i in range(int(page)):
        file_s='temp/'+str(i)+'.jpg'
        print('开始上传图片:'+file_s)
        try:
            b=upload(formatSource(file_s))
        except:
            continue
        os.remove(file_s)
        img_hc='<img src="'+b['image']['url']+'">'
        with open('temp/temp.txt','a+') as f:
            f.write(img_hc)

def post_article(tittle):
    with open('temp/temp.txt','r') as f:
        wz_content=f.read()
    with open('temp/tj.txt','r') as f:
        wzs=f.read()
    k=int(wzs)
    a=wordpress_post(str(tittle[0]),wz_content)
    conn=a.mysql_con()
    cursor = conn.cursor()
    c=a.up()
    effect_row = cursor.execute(c)
    new_id = cursor.lastrowid
    d=a.cat(new_id,'1') #文章分类，去wp_term_taxonomy里找你需要的id
    effect_row = cursor.execute(d)
    a.close_mysql(cursor,conn)
    print('文章已发布:'+tittle[0])
    os.remove('temp/temp.txt')
    k+=1
    j=str(k)
    with open('temp/tj.txt','w+') as f:
        f.write(j)
 
def main():
    flag=1
    while flag<=270:
        base_url='https://t66y.com/'
        page_url='https://t66y.com/thread0806.php?fid=8&search=&page='+str(flag)
        get=requests.get(page_url)
        article_url=re.findall(r'<h3><a href="(.*)" target="_blank" id="">(?!<.*>).*</a></h3>',str(get.content,'gbk',errors='ignore'))
        for url in article_url:
            threads=[]
            tittle=['default']
            getpage=requests.get(str(base_url)+str(url))
            tittle=re.findall(r'<h4>(.*)</h4>',str(getpage.content,'gbk',errors='ignore'))
            file=tittle[0]
            img_url=re.findall(r'<input src=\'(.*?)\'',str(getpage.content,'gbk',errors='ignore'))
            filename=1
            print('开始下载：'+file)
            for download_url in img_url:
                thread=myThread(download_url,file,filename)
                thread.start()
                threads.append(thread)
                filename=filename+1
            for t in threads:
                t.join()
            print('下载完成，共'+str(filename)+'张图片')
            print('开始上传图片')
            try:
                upload_img(filename,tittle)
            except:
                print('图床错误')
                continue
            post_article(tittle)
            time.sleep(60)
        print('第'+str(flag)+'页下载完成')
        flag=flag+1
        
if __name__=='__main__':
    try:
        if os.path.exists('temp')==False:
            os.makedirs('temp')
            f=open('temp/tj.txt','w+')
            f.close()
            with open('temp/tj.txt','w+') as f:
                f.write('0')
            main()
        else:
            main()
    except:
        print('主程序出错，请重新运行')
        
#tj.txt里记录了采集了多少篇，可以用来更新wp_term_taxonomy中对应项的count值（如果这个分类里只有采集的话）