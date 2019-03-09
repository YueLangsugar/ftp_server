###服务器
###ftp_server.py
##文件服务器
from socket import *
import signal,os,sys,time
Host = '0.0.0.0'
Post = 9696
address = (Host,Post)
content = '/home/tarena/pythonnet/practice/'

class FtpServer(object):
    def __init__(self,c):
        self.c = c

    def do_get(self,filename):      ##客户端上传文件
        file_list = os.listdir(content)
        if filename in file_list:
            self.c.send("文件重名".encode())
        else:
            self.c.send(b'OK')
            time.sleep(0.1)

        fw = open(content+filename,'wb')
        while True:
            #time.sleep(0.1)
            file_data = self.c.recv(1024)
            if file_data == b'$$':
                break
            fw.write(file_data)
        fw.close()
        
    def do_put(self,filename):   ##客户端下载文件
        try:
            fd = open(content+filename,'rb')
        except IOError:
            self.c.send("文件不存在".encode())
            return
        else:
            self.c.send(b'OK')
            time.sleep(0.2)
        ##发送文件内容
        while True:
            file_data = fd.read(1024)
            if not file_data:
                time.sleep(0.2)
                self.c.send(b'$$')
                break
            self.c.send(file_data)
        fd.close()


    def do_list(self):
        ##获取文件列表
        file_list = os.listdir(content)
        if not file_list:
            self.c.send("文件库为空".encode())
            return 
        self.c.send(b'OK')
        time.sleep(0.2)
        files = ""
        for file in file_list:
            if file[0] != '.' and os.path.isfile(content+file):
                files = files+file+'#'
        ##将拼接好的字符串传给客户端
        self.c.send(files.encode())

def do_request(c):
    ftp = FtpServer(c)
    while True:
        data = c.recv(1024).decode()
        if not data or data[0] == 'Q':
            c.close()
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':    ##客户端下载文件
            filename = data.split(' ')[-1]
            ftp.do_put(filename)
        elif data[0] == 'P':    ###客户端上传文件
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        

def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) ##端口可重用
    s.bind(address)
    s.listen(5)
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()   ##连接成功
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue
        print("Connect from:",addr)

        pid = os.fork()

        if pid == 0:  ##子进程
            s.close()
            do_request(c)   ###处理客户端的请求
            os._exit(0)

        else:
            c.close()

if __name__ == "__main__":
    main()