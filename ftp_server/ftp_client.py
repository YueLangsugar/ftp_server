from socket import *
import sys,time,os

content = '/home/tarena/pythonnet/day08_net'

server_addr = (('0.0.0.0',9696))
##具体功能
class FtpClient(object):
    def __init__(self,s):
        self.s = s  ###套接字
    
    def do_put(self,filename):  ##客户端上传文件
        ##获取真实文件名,对路径解析
        fileno = filename.split('/')[-1]
        ##获取文件路径
        pathlist = filename.split('/')[0:-1]
        if len(pathlist) != 0:
            path = '/'.join(pathlist)
        else:
            path = content

        if not os.path.exists(path+'/'+fileno):   ##判断输入文件是否存在实际路径中
            print("文件不存在或者文件名错误")
            return

        self.s.send(('P '+fileno).encode())       ##有瑕疵，文件名大意输错了导致文件不存在怎么办
        data = self.s.recv(128).decode()
        if data == 'OK':    ##文件名不重复，可以上传
            try:
                fr = open(path+'/'+fileno,'rb')
            except IOError:
                print("文件不存在")
                return 
            while True:
                file_data = fr.read(1024)
                if not file_data:
                    time.sleep(0.1)
                    self.s.send(b'$$')
                    break
                self.s.send(file_data)
                
            fr.close()
        else:
            print(data)
                   
    def do_get(self,filename):      ##客户端下载文件
        self.s.send(('G '+filename).encode())
        data = self.s.recv(128).decode()
        if data == 'OK':
            fd = open(filename,'wb')
            while True:
                file_data = self.s.recv(1024)
                if file_data == b'$$':
                    break
                fd.write(file_data)
            fd.close()
        else:
            print(data)
    
    def do_list(self):
        self.s.send(b'L')  ##发送请求
        ##等待回复
        data = self.s.recv(128).decode()
        if data == 'OK':
            file_data = self.s.recv(4096).decode()
            files = file_data.split('#')
            for file in files:
                print(file)
        else:
            ##无法完成
            print(data)
    
    def do_quit(self):
        self.s.send(b'Q')
        self.s.close()
        sys.exit("谢谢使用")
    
def menu():
    print("------------请选择你的操作------------")
    print("------------1.查看文件库中的文件list------------")
    print("------------2.下载文件get file------------")
    print("------------3.上传文件put file------------")
    print("------------4.退出quit------------")

#def show_file(self,s):

##网络连接
def main():
    s = socket()
    try:
        s.connect(server_addr)
    except Exception as e:
        print("连接服务器失败:",e)
        return 

    ##创建文件处理类对象
    ftp = FtpClient(s)

    while True:
        menu()
        cmd = input("输入命令>>")
        if cmd.strip() == 'list':
            ftp.do_list()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1]   ##获取文件名
            ftp.do_get(filename)
        elif cmd[:3] == 'put':  ##上传客户端文件
            filename = cmd.strip().split(' ')[-1] 
            ftp.do_put(filename)
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        else:
            print("输入指令错误")
            continue

if __name__ == "__main__":
    main()